#include "WiFi.h"
#include "esp_camera.h"

//
// --- PIN DEFINITIONS (for AI-THINKER board) ---
//
#define PWDN_GPIO_NUM     32
#define RESET_GPIO_NUM    -1
#define XCLK_GPIO_NUM      0
#define SIOD_GPIO_NUM     26
#define SIOC_GPIO_NUM     27
#define Y9_GPIO_NUM       35
#define Y8_GPIO_NUM       34
#define Y7_GPIO_NUM       39
#define Y6_GPIO_NUM       36
#define Y5_GPIO_NUM       21
#define Y4_GPIO_NUM       19
#define Y3_GPIO_NUM       18
#define Y2_GPIO_NUM        5
#define VSYNC_GPIO_NUM    25
#define HREF_GPIO_NUM     23
#define PCLK_GPIO_NUM     22

//
// --- CONFIGURATION ---
//
const char* ssid = "HackTheNorth";
const char* password = "HTN2025!";
const char* server_ip = "10.37.126.214"; // ❗️ IMPORTANT: CHANGE THIS to your PC's IP address
const int server_port = 9000;

const int WIFI_CHANNEL = 6;  // Use a less crowded channel (1-13)
const int WIFI_CHANNEL_WIDTH = 40;  // 40MHz channel width
const int WIFI_MAX_TX_POWER = 84;  // Max power (20dBm)

WiFiClient client;

// Helper function to get current timestamp as a string
String getTimestamp() {
  unsigned long ms = millis();
  unsigned long secs = ms / 1000;
  unsigned long mins = secs / 60;
  unsigned long hours = mins / 60;
  char timestamp[13]; // [HH:MM:SS.mmm]
  snprintf(timestamp, sizeof(timestamp), "[%02lu:%02lu:%02lu.%03lu]", 
           hours % 24, mins % 60, secs % 60, ms % 1000);
  return String(timestamp);
}

void setupCamera() {
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sccb_sda = SIOD_GPIO_NUM;
  config.pin_sccb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 10000000;
  config.frame_size = FRAMESIZE_UXGA;
  config.pixel_format = PIXFORMAT_JPEG;
  config.grab_mode = CAMERA_GRAB_WHEN_EMPTY;
  config.fb_location = CAMERA_FB_IN_PSRAM;
  config.jpeg_quality = 50;
  config.fb_count = 1;

  if (esp_camera_init(&config) != ESP_OK) {
    Serial.printf("%s Camera init failed!\n", getTimestamp().c_str());
    return;
  }
}

void setup() {
  Serial.begin(115200);
  
  // Optimize WiFi settings
  WiFi.mode(WIFI_STA);
  WiFi.setSleep(false);
  WiFi.setTxPower(WIFI_POWER_19_5dBm);
  
  // Advanced WiFi configuration
  WiFi.setAutoReconnect(true);
  // esp_wifi_set_bandwidth(ESP_IF_WIFI_STA, WIFI_BW_HT40);  // 40MHz channel width
  // esp_wifi_set_channel(WIFI_CHANNEL, WIFI_SECOND_CHAN_NONE);
  
  // Set WiFi protocol to 802.11n only
  // esp_wifi_set_protocol(ESP_IF_WIFI_STA, WIFI_PROTOCOL_11N);
  
  // Set MCS (Modulation and Coding Scheme) to 7 (highest)
  wifi_interface_t ifx = WIFI_IF_STA;
  uint8_t mcs_rate = 7;
  // esp_wifi_config_11n_rate(ifx, true, mcs_rate);
  
  WiFi.begin(ssid, password);
  Serial.printf("%s Connecting to WiFi...", getTimestamp().c_str());
  while (WiFi.status() != WL_CONNECTED) {
    delay(100);
    Serial.print(".");
  }
  Serial.printf("\n%s WiFi connected\n", getTimestamp().c_str());
  Serial.printf("%s ESP32 IP Address: ", getTimestamp().c_str());
  Serial.println(WiFi.localIP());

  setupCamera();
}

void loop() {
  // If not connected, try to connect to the server
  if (!client.connected()) {
    Serial.printf("%s Attempting to connect to server %s:%d...", 
                 getTimestamp().c_str(), server_ip, server_port);
    if (!client.connect(server_ip, server_port)) {
      Serial.printf("%s Connection failed. Retrying in 2 seconds...\n", getTimestamp().c_str());
      delay(500);
      return;
    }
    Serial.printf("\n%s Connected to server!\n", getTimestamp().c_str());
  }

  // Check if the server has sent a command
  if (client.available()) {
    String cmd = client.readStringUntil('\n');
    cmd.trim();
    Serial.printf("%s Received command: '%s'\n", getTimestamp().c_str(), cmd.c_str());
    camera_fb_t* fb = esp_camera_fb_get();

    if (cmd == "GET_FRAME") {
      if (!fb) {
        Serial.printf("%s Camera capture failed\n", getTimestamp().c_str());
        client.println("ERR Capture Failed");
        return;
      }
      
      // 1. Send the size header, followed by a newline
      client.printf("SIZE %zu\n", fb->len);
      Serial.printf("%s Sending frame, size: %zu bytes\n", getTimestamp().c_str(), fb->len);
      
      // 2. Send the raw image data in larger chunks
      const size_t CHUNK_SIZE = 16 * 1024;  // 16KB chunks
      size_t to_send = fb->len;
      const uint8_t* buf_ptr = fb->buf;
      size_t total_sent = 0;
      uint32_t start_time = millis();
      uint32_t last_print = start_time;
      
      while (to_send > 0 && client.connected()) {
        size_t chunk = min(to_send, CHUNK_SIZE);
        size_t sent = client.write(buf_ptr, chunk);
        
        if (sent == 0) {
          if (millis() - start_time > 20000) {  // 20s timeout
            Serial.printf("%s Send timeout\n", getTimestamp().c_str());
            break;
          }
          delay(1);
          continue;
        }
        
        total_sent += sent;
        buf_ptr += sent;
        to_send -= sent;
        
        // Print progress every 500ms
        uint32_t now = millis();
        if (now - last_print >= 500) {
          float progress = (total_sent * 100.0f) / fb->len;
          float elapsed = (now - start_time) / 1000.0f;
          float rate = (total_sent * 8.0f) / (now - start_time);  // kbps
          
          Serial.printf("%s Progress: %.1f%% (%.1f kbps)\n", 
                       getTimestamp().c_str(), progress, rate);
          last_print = now;
        }
        
        // Small yield to prevent WDT
        if (total_sent % (CHUNK_SIZE * 4) == 0) {
          yield();
        }
      }
      
      uint32_t duration = millis() - start_time;
      float rate_kbps = (total_sent * 8.0f) / (duration > 0 ? duration : 1);
      
      if (to_send == 0) {
        Serial.printf("%s Frame sent successfully in %.2fs (%.2f kbps)\n", 
                     getTimestamp().c_str(), duration/1000.0f, rate_kbps);
      } else {
        Serial.printf("%s Sent %zu/%zu bytes in %.2fs (%.2f kbps)\n", 
                     getTimestamp().c_str(), total_sent, fb->len, 
                     duration/1000.0f, rate_kbps);
      }
    }

    esp_camera_fb_return(fb);
  }
  
  delay(10); // Small delay to yield to other tasks
}
