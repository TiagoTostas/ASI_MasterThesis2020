#include "stdint.h"
#include "stdio.h"
#include "app_act.h"
#include "math.h"

typedef struct{
	uint32_t rpeaks;
  uint16_t heartrate;
	uint16_t rr_intervals;
} heartrateStruct;



int16_t fir_filt_circ_buff(int16_t x);
uint32_t peak_detector(int16_t ecg_filtered);
void heartrate_new(heartrateStruct *hralgoStruct_var);

