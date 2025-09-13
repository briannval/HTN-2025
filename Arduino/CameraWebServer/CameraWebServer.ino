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

WiFiClient client;

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
  config.xclk_freq_hz = 20000000;
  config.frame_size = FRAMESIZE_UXGA;
  config.pixel_format = PIXFORMAT_JPEG;
  config.grab_mode = CAMERA_GRAB_WHEN_EMPTY;
  config.fb_location = CAMERA_FB_IN_PSRAM;
  config.jpeg_quality = 50;
  config.fb_count = 1;

  if (esp_camera_init(&config) != ESP_OK) {
    Serial.println("Camera init failed!");
    return;
  }
}

void setup() {
  Serial.begin(115200);
  
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi...");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\n✅ WiFi connected");
  Serial.print("ESP32 IP Address: ");
  Serial.println(WiFi.localIP());

  setupCamera();
}

void loop() {
  // If not connected, try to connect to the server
  if (!client.connected()) {
    Serial.printf("\nAttempting to connect to server %s:%d...", server_ip, server_port);
    if (!client.connect(server_ip, server_port)) {
      Serial.println("Connection failed. Retrying in 2 seconds...");
      delay(2000);
      return;
    }
    Serial.println("\n✅ Connected to server!");
  }

  // Check if the server has sent a command
  if (client.available()) {
    String cmd = client.readStringUntil('\n');
    cmd.trim();
    Serial.printf("Received command: '%s'\n", cmd.c_str());
    camera_fb_t* fb = esp_camera_fb_get();

    if (cmd == "GET_FRAME") {
      if (!fb) {
        Serial.println("Camera capture failed");
        client.println("ERR Capture Failed");
        return;
      }
      
      // 1. Send the size header, followed by a newline
      client.printf("SIZE %zu\n", fb->len);
      Serial.printf("Sent header: SIZE %zu\n", fb->len);
      
      // 2. Send the raw image data
      client.write(fb->buf, fb->len);
      client.flush(); // Flush the buffer to make sure data is sent
      Serial.printf("Sent %zu bytes of image data.\n", fb->len);
      // We DO NOT close the connection here.
      // The ESP32 is now ready for the next GET_FRAME command.
    }

    esp_camera_fb_return(fb);
  }
  
  delay(10); // Small delay to yield to other tasks
}
