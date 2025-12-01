#ifndef UTILITY_FUNCTIONS_H
#define UTILITY_FUNCTIONS_H

//// define a mean function
float mean(float values[], int numValues) {
  float sum = 0.0;
  for (int i = 0; i < numValues; i++) {
    sum += values[i];
  }
  return sum / numValues;
}

//// define a low-pass (exponantial) filter function
float calc_exponatial_filter(float value_new, float value_previous, float smooth_factor){
  float value_filtered = smooth_factor*value_new + (1-smooth_factor)*value_previous;
  return value_filtered;
}

//// define a median filter function
float calc_median_outlier_filter(float a, float b, float c) {
  if ((a <= b && b <= c) || (c <= b && b <= a)) return b;
  if ((b <= a && a <= c) || (c <= a && a <= b)) return a;
  return c;
}

//// define a sign function
int sign(float x) {
  return (x > 0) - (x < 0);
}

#endif