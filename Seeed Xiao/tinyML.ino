
#include <TensorFlowLite.h>
#include "tensorflow/lite/micro/all_ops_resolver.h"
#include "tensorflow/lite/micro/micro_error_reporter.h"
#include "tensorflow/lite/micro/micro_interpreter.h"
#include "tensorflow/lite/schema/schema_generated.h"

#include "model.h"

#define LED LEDG
#define WIDTH 129
#define HEIGHT 71

tflite::ErrorReporter* error_reporter;
const int tensor_arena_size = 90000;
uint8_t tensor_arena[tensor_arena_size];
tflite::MicroInterpreter* interpreter;
const tflite::Model *model;
TfLiteTensor* input;
TfLiteTensor* output;

float spectogram[WIDTH * HEIGHT];

void setup() {
  delay(5000);
  pinMode(LED, OUTPUT);
  digitalWrite(LED, HIGH);
  Serial.begin(9600);

  tflite::MicroErrorReporter micro_error_reporter;
  tflite::ErrorReporter* error_reporter = &micro_error_reporter;

  model = ::tflite::GetModel(model_tflite);
  if (model->version() != TFLITE_SCHEMA_VERSION) {
  TF_LITE_REPORT_ERROR(error_reporter,
      "Model provided is schema version %d not equal "
      "to supported version %d.\n",
      model->version(), TFLITE_SCHEMA_VERSION);
  }

  static tflite::AllOpsResolver resolver;
  
  static tflite::MicroInterpreter static_interpreter = tflite::MicroInterpreter(model, resolver, tensor_arena,
                                     tensor_arena_size, error_reporter);
  interpreter = &static_interpreter;

  TfLiteStatus allocation_status = interpreter->AllocateTensors();
  if (allocation_status == kTfLiteError){
    Serial.println("Tensor arena allocation failed!");
    return;
  }

  input = interpreter->input(0);
  output = interpreter->output(0);
              
  Serial.println("Success!");
}

void loop() {
  delay(500);
  digitalWrite(LED, HIGH);

  input->data.f = spectogram;
  TfLiteStatus invoke_status = interpreter->Invoke();
  if (invoke_status != kTfLiteOk) {
    TF_LITE_REPORT_ERROR(error_reporter, "Invoke failed\n");
  }

  float result = output->data.f[0];

  Serial.print("Prediction: ");
  Serial.println(result);

  delay(500);
  digitalWrite(LED, LOW);
}
