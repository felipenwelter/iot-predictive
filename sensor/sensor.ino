#include <stdio.h> 
#include <string.h>

/* Header para funções de Wi-Fi do ESP32 */
#include <WiFi.h>

/* Header de bibliotecas para MQTT */
#include <PubSubClient.h>  
#include <ArduinoJson.h>

/* Header para sensor MPU-6050 */
#include <Wire.h>
#include <Kalman.h>
#define RESTRICT_PITCH //Comment out to restrict roll to ±90deg instead

/*------------------------------------------*/

/*Define saída no monitor*/
#define DEBUG_UART_BAUDRATE        115200

/*Defines do MQTT*/
#define MQTT_PUB_TOPIC_TEMP "equipment/temperature" //envio de dados
#define MQTT_PUB_TOPIC_VIBRATION "equipment/vibration" //envio de dados
#define MQTT_SUB_TOPIC "equipment/actions" //recebimento de dados
#define MQTT_ID "xpto-equipment"  //identificador do equipamento

/*------------------------------------------*/

/*Variáveis globais do Wi-Fi e MQTT*/
const char* ssid_wifi = "2.4 IVANILDE";  //"Felipe";
const char* password_wifi = "07021622";
const char* broker_mqtt = "192.168.0.25"; //endereço do broker MQTT
int broker_port = 1883; //porta para o broker MQTT

WiFiClient espClient;     //objeto para conexao com internet
PubSubClient MQTT(espClient); //objeto para conexao com broker

/*Variáveis para sincronismo de data de hora (NTP)*/
const char* ntpServer = "pool.ntp.org";
const long  gmtOffset_sec = -10800; //(GMT-3);
const int   daylightOffset_sec = 0; //daylight saving time (if uses set 3600)
//unsigned long lastmili;
//unsigned long currentmili;

/*Define os pinos GPIO para LEDs*/
const int pinoLED_green = 5;
const int pinoLED_yellow = 17;
const int pinoLED_red = 16;

/*Variáveis para contorle do MPU6050-----------------------------------*/
Kalman kalmanX;
Kalman kalmanY;

double accX, accY, accZ;
double gyroX, gyroY, gyroZ;
int16_t tempRaw;

double gyroXangle, gyroYangle; // Angle calculate using the gyro only
double compAngleX, compAngleY; // Calculated angle using a complementary filter
double kalAngleX, kalAngleY; // Calculated angle using a Kalman filter

uint32_t timer;
uint8_t i2cData[14]; // Buffer for I2C data

double mpu_roll[50];
double mpu_pitch[50];

char buffer_roll[400];
char buffer_pitch[400];
char buffer_temp[8];

typedef struct
{
    char date_time[256];
    double pitch;
    double roll;
} measure_struct; 

measure_struct vibration_measures[12];
int loop_temp = 0;
int vibration_count = -1;
/*---------------------------------------------------------------------*/

/* Prototypes */
void init_wifi(void);
void init_MQTT(void);
void connect_MQTT(void);
void connect_wifi(void);
void verify_wifi_connection(void);
void mqtt_callback(char* topic, byte* payload, unsigned int length); 

/*------------------------------------------*/

/* Função: Inicaliza conexão wi-fi
 * Parâmetros: Nenhum
 * Retorno: Nenhum 
 */
void init_wifi(void) 
{
   delay(10);
   
   /*apaga LEDs enquanto conecta*/
   digitalWrite(pinoLED_green,LOW);
   digitalWrite(pinoLED_yellow,LOW);
   digitalWrite(pinoLED_red,LOW);
    
   Serial.println("------ WI-FI -----");
   Serial.print("Tentando se conectar a seguinte rede wi-fi: ");
   Serial.println(ssid_wifi);
   Serial.println("Aguarde");    
   
   connect_wifi();
}

/* Função: Conecta com a rede wifi
 * Parâmetros: Nenhum
 * Retorno: Nenhum 
 */
void connect_wifi(void) 
{
   while (WiFi.status() != WL_CONNECTED) {
      WiFi.begin(ssid_wifi, password_wifi);
      delay(1000);
      Serial.print(".");
   }
}

/* Função: Verifica se há conexão wi-fi ativa (e conecta-se caso não haja)
 * Parâmetros: Nenhum
 * Retorno: Nenhum 
 */
void verify_wifi_connection(void)
{
   connect_wifi(); 
}

/* Função: Configura endereço do broker e porta para conexão com broker MQTT
 * Parâmetros: Nenhum
 * Retorno: Nenhum 
 */
void init_MQTT(void)
{
   MQTT.setServer(broker_mqtt, broker_port);
   
   /* Informa que todo dado que chegar do broker pelo tópico definido em MQTT_SUB_TOPIC
      Irá fazer a função mqtt_callback ser chamada*/
   MQTT.setCallback(mqtt_callback);
   
    /*Redimensiona buffer MQTT para envio dos pacotes JSON*/
   if (!MQTT.setBufferSize(1024))
      Serial.println("couldn't resize buffer");
}

/* Função: Conecta-se ao broker MQTT (se não há conexão já ativa)
 * Parâmetros: Nenhum
 * Retorno: Nenhum 
 */
void connect_MQTT(void) 
{
   while (!MQTT.connected()) 
   {
      Serial.print("* Tentando se conectar ao seguinte broker MQTT: ");
      Serial.println(broker_mqtt);
        
      if (MQTT.connect(MQTT_ID)) 
      {
         Serial.println("Conexao ao broker MQTT feita com sucesso!");
         /* Após conexão, se subescreve no tópico definido por MQTT_SUB_TOPIC.
            Dessa forma, torna possível receber informações do broker por 
            este tópico. */
         MQTT.subscribe(MQTT_SUB_TOPIC);
      } 
      else 
      {
         Serial.println("Falha ao se conectar ao broker MQTT.");
         Serial.println("Nova tentativa em 2s...");
         delay(2000);
      }
   }
}

/*Função: Função de callback, chamada toda vez que chegam dados
*         pelo tópico definido em MQTT_SUB_TOPIC
* Parâmetros: Nenhum
* Retorno: Nenhum
*/
void mqtt_callback(char* topic, byte* payload, unsigned int length) 
{
   String msg_broker;
   char c;

   StaticJsonDocument<256> jsonActions;

   //Data formatting:
   //send: {"action":"configure"}
   //send: {"action":"status", "vibration_level": 0/1/2/3}
    
   // Publish the message
   char buff[256];
   char action[10];
   int level = -1;
    
   deserializeJson(jsonActions, payload);
   strcpy(action, jsonActions["action"]);
   level = jsonActions["vibration_level"];
    
   /*------------------------*/
   if (strncmp(action,"configure",9) == 0) {
      digitalWrite(pinoLED_green,HIGH);
      digitalWrite(pinoLED_yellow,HIGH);
      digitalWrite(pinoLED_red,HIGH);
   }else{

      if (strncmp(action,"status",6) == 0) {
            
         Serial.println(level);
            
         if (level == 0){
            digitalWrite(pinoLED_green,LOW);
            digitalWrite(pinoLED_yellow,LOW);
            digitalWrite(pinoLED_red,LOW);
         }
         if (level == 1){
            digitalWrite(pinoLED_green,LOW);
            digitalWrite(pinoLED_yellow,HIGH);
            digitalWrite(pinoLED_red,LOW);
         }
         if (level == 2){
            digitalWrite(pinoLED_green,HIGH);
            digitalWrite(pinoLED_yellow,LOW);
            digitalWrite(pinoLED_red,LOW);
         }
         if (level == 3){
            digitalWrite(pinoLED_green,LOW);
            digitalWrite(pinoLED_yellow,LOW);
            digitalWrite(pinoLED_red,HIGH);
         }
          
      }else{
         digitalWrite(pinoLED_green,LOW);
         digitalWrite(pinoLED_yellow,LOW);
         digitalWrite(pinoLED_red,LOW);
      }
       
   }
   //delay(300);
}

/*Função: Setup, configurações iniciais ao ligar o ESP32
* Parâmetros: Nenhum
* Retorno: Nenhum
*/
void setup() 
{
   /* Configuração da serial (usada para debug no Serial Monitor) */  
   Serial.begin(DEBUG_UART_BAUDRATE);

   /*Define utilização dos pinos GPIO para LEDs*/
   pinMode(pinoLED_green,OUTPUT);
   pinMode(pinoLED_yellow,OUTPUT);
   pinMode(pinoLED_red,OUTPUT);
    
   /*Inicializa conexão wi-fi */
   init_wifi();

   /*Sincroniza relogio com NTP Server*/
   configTime(gmtOffset_sec, daylightOffset_sec, ntpServer);
   delay(5000);
    
   /* inicializa conexão MQTT */
   init_MQTT();
   connect_MQTT();
    
   /*Inicializa configurações do MPU6050*/
   Wire.begin();
   #if ARDUINO >= 157
      Wire.setClock(400000UL); // Define frequencia I2C para 400kHz
   #else
      TWBR = ((F_CPU / 400000UL) - 16) / 2; // Define frequencia I2C para 400kHz
   #endif
    
   i2cData[0] = 7; // Set the sample rate to 1000Hz - 8kHz/(7+1) = 1000Hz
   i2cData[1] = 0x00; // Disable FSYNC and set 260 Hz Acc filtering, 256 Hz Gyro filtering, 8 KHz sampling
   i2cData[2] = 0x00; // Set Gyro Full Scale Range to ±250deg/s
   i2cData[3] = 0x00; // Set Accelerometer Full Scale Range to ±2g
   while (i2cWrite(0x19, i2cData, 4, false)); // Write to all four registers at once
   while (i2cWrite(0x6B, 0x01, true)); // PLL with X axis gyroscope reference and disable sleep mode
    
   while (i2cRead(0x75, i2cData, 1));
   if (i2cData[0] != 0x68) { // Read "WHO_AM_I" register
     Serial.print(F("Error reading sensor"));
     while (1);
   }
    
   delay(100); // Espera sensor estabilizar
    
   /* Set kalman and gyro starting angle */
   while (i2cRead(0x3B, i2cData, 6));
   accX = (int16_t)((i2cData[0] << 8) | i2cData[1]);
   accY = (int16_t)((i2cData[2] << 8) | i2cData[3]);
   accZ = (int16_t)((i2cData[4] << 8) | i2cData[5]);
    
   // Source: http://www.freescale.com/files/sensors/doc/app_note/AN3461.pdf eq. 25 and eq. 26
   // atan2 outputs the value of -π to π (radians) - see http://en.wikipedia.org/wiki/Atan2
   // It is then converted from radians to degrees
   #ifdef RESTRICT_PITCH // Eq. 25 and 26
      double roll  = atan2(accY, accZ) * RAD_TO_DEG;
      double pitch = atan(-accX / sqrt(accY * accY + accZ * accZ)) * RAD_TO_DEG;
   #else // Eq. 28 and 29
      double roll  = atan(accY / sqrt(accX * accX + accZ * accZ)) * RAD_TO_DEG;
      double pitch = atan2(-accX, accZ) * RAD_TO_DEG;
   #endif
    
   kalmanX.setAngle(roll); // Set starting angle
   kalmanY.setAngle(pitch);
   gyroXangle = roll;
   gyroYangle = pitch;
   compAngleX = roll;
   compAngleY = pitch;
    
   timer = micros();
   //lastmili = millis();
   /*------------------------------------------*/

   //Tanto o SETUP quanto as funções principais do LOOP são executadas com prioridade de 1 e no núcleo 1.
   //Prioridades podem ir de 0 a N, onde 0 é a menor prioridade. Núcleo pode ser 0 ou 1.

   //cria uma tarefa que será executada na função coreTaskZero, com prioridade 1 e execução no núcleo 0
   xTaskCreatePinnedToCore(
          receive_data,   /* função que implementa a tarefa */
          "coreTaskZero", /* nome da tarefa */
          10000,      /* número de palavras a serem alocadas para uso com a pilha da tarefa */
          NULL,       /* parâmetro de entrada para a tarefa (pode ser NULL) */
          1,          /* prioridade da tarefa (0 a N) */
          NULL,       /* referência para a tarefa (pode ser NULL) */
          0);         /* Núcleo que executará a tarefa */

}

/*Função: Loop para recebimento de dados via MQTT
* Parâmetros: Nenhum
* Retorno: Nenhum
*/
void receive_data( void * pvParameters ){
  
   while(true){
      delay(100);
      /* Keep-alive do MQTT */
      MQTT.loop(); 
    } 
}

/*Função: Função principal executada em loop
* Parâmetros: Nenhum
* Retorno: Nenhum
*/
void loop() 
{

   /* Update all the values */
   while (i2cRead(0x3B, i2cData, 14));
   accX = (int16_t)((i2cData[0] << 8) | i2cData[1]);
   accY = (int16_t)((i2cData[2] << 8) | i2cData[3]);
   accZ = (int16_t)((i2cData[4] << 8) | i2cData[5]);
   tempRaw = (int16_t)((i2cData[6] << 8) | i2cData[7]);
   gyroX = (int16_t)((i2cData[8] << 8) | i2cData[9]);
   gyroY = (int16_t)((i2cData[10] << 8) | i2cData[11]);
   gyroZ = (int16_t)((i2cData[12] << 8) | i2cData[13]);;
   
   double dt = (double)(micros() - timer) / 1000000; // Calculate delta time
   timer = micros();
   
   // Source: http://www.freescale.com/files/sensors/doc/app_note/AN3461.pdf eq. 25 and eq. 26
   // atan2 outputs the value of -π to π (radians) - see http://en.wikipedia.org/wiki/Atan2
   // It is then converted from radians to degrees
   #ifdef RESTRICT_PITCH // Eq. 25 and 26
      double roll  = atan2(accY, accZ) * RAD_TO_DEG;
      double pitch = atan(-accX / sqrt(accY * accY + accZ * accZ)) * RAD_TO_DEG;
   #else // Eq. 28 and 29
      double roll  = atan(accY / sqrt(accX * accX + accZ * accZ)) * RAD_TO_DEG;
      double pitch = atan2(-accX, accZ) * RAD_TO_DEG;
   #endif

   double temperature = (double)tempRaw / 340.0 + 36.53;

   /* Verifica se a conexão wi-fi está ativa e, em caso negativo, reconecta-se ao roteador */
   verify_wifi_connection();
   /* Verifica se a conexão ao broker MQTT está ativa e, em caso negativo, reconecta-se ao broker */
   connect_MQTT();
   /* Envia a ifrase "Comunicacao MQTT via ESP32" via MQTT */

   //incrementa controle dos ciclos
   loop_temp++;

   vibration_count++;

   //Serial.println(temperature);
    
   /* get and format date and time-------------*/
   char date_time[256];
   int time_len = 0;
   struct tm *tm_info;
   struct timeval tv;
    
   gettimeofday(&tv, NULL);
   tm_info = localtime(&tv.tv_sec);
   time_len+=strftime(date_time, sizeof(date_time), "%d-%b-%Y %H:%M:%S", tm_info);
   time_len+=snprintf(date_time+time_len,sizeof(date_time)-time_len,".%06ld ",tv.tv_usec);
   /*------------------------------------------*/
   delay(50);
   vibration_measures[vibration_count].pitch = pitch;
   vibration_measures[vibration_count].roll = roll;
   strcpy(vibration_measures[vibration_count].date_time, date_time);

   if (vibration_count == 11 ){ 

      DynamicJsonDocument jsonVibration(2048);
      jsonVibration["Sensor_ID"] = "equipment-001";

      JsonArray measure = jsonVibration.createNestedArray("measure");

      for (int i = 0; i <= 11; i++){
         StaticJsonDocument<512> jsonMeasure;
         jsonMeasure["Date"] = vibration_measures[i].date_time;
         jsonMeasure["Pitch"] = vibration_measures[i].pitch;
         jsonMeasure["Roll"] = vibration_measures[i].roll;
         measure.add(jsonMeasure);
         jsonMeasure.clear();
      }
        
      // Publish the message
      char buffer_vibration[2048];
      size_t n = serializeJson(jsonVibration, buffer_vibration);
      MQTT.publish(MQTT_PUB_TOPIC_VIBRATION, buffer_vibration, n);
  
      vibration_count = -1;
      serializeJson(jsonVibration, buffer_vibration);

      //currentmili = millis();
      //Serial.println(currentmili-lastmili);
      //lastmili = currentmili;
      
   }

   
   if (loop_temp >= 600 ){  // a cada 30 segundos manda temperatura
        
      StaticJsonDocument<512> jsonTemperature;
        
      jsonTemperature["Sensor_ID"] = "equipment-001";
      jsonTemperature["Date"] = date_time;
      jsonTemperature["Temperature"] = temperature;
        
      // Publish the message
      char buffer_temperature[512];
      size_t n = serializeJson(jsonTemperature, buffer_temperature);
      MQTT.publish(MQTT_PUB_TOPIC_TEMP, buffer_temperature, n);

      loop_temp = 0;
      //serializeJson(jsonTemperature, buffer_temperature);
   }


}
