/***************************************************/
#include "HR_algo.h"
#include "math.h"
#include "app_act.h"


//definitionn for FS 250Hz
#define freq_sample 250
#define ND 5
#define tf1 50   
#define expon 0.98
#define aaa 0.95
#define bbb 0.05
#define buffer_lenght 5 // number of sample needed

void shift_left_array(int16_t* array1, uint32_t* array2, uint8_t len ){
	for(uint8_t i=0; i < 4;  i++) {
		if (array1 != NULL)
				array1[i] = array1[i+1];
		if (array2 != NULL)
			array2[i] = array2[i+1];
	}
}
	
uint32_t peak_detector(int16_t rawECG ){ 				//input ADC sample and sample frequency
	
	//buffer def
	static uint32_t i_rpeaks = 0;
	static int32_t diff[2];
	static int32_t ddiff;
	static uint32_t squar [buffer_lenght];
	static uint8_t i_squar = 0;
	static uint32_t processed_ecg;
	static int16_t buffer_ECG[buffer_lenght];  /// record last 5 samples
	
	//adaptive detection threshold
	static uint32_t rpeakpos = 0;
	
	//variables  for finite state machine
	static float Rpeakamp = 0;
	static float Ramptotal = 0;
	static float threshold = 0   ; // threshold for state 3
	static uint32_t	counter = 6 ;  // sets duration in each state, starting at 6 to account for delay with the buffers
	static uint32_t	d = 0 ;
	static uint32_t	tf2 = 0;			 // time for state 2
	static uint8_t	state = 1 ;		 // fsm starts at state 1												

	//for the RR-intervals
	static uint32_t last_peak = 0;
	
	/* buffering first  ND samples*/
	if (i_rpeaks < (buffer_lenght-1)){

			buffer_ECG[i_rpeaks] = rawECG;
			i_rpeaks++;
		
		return 0;
	}
	else {
		buffer_ECG[buffer_lenght-1] = rawECG;	
	}

		/*preprocessing if more than  ND samples */
		diff[1] = buffer_ECG[ ND - 1 ] - buffer_ECG[0];  
		ddiff = diff[1] - diff[0];
	
		//shift diff value
		diff[0] = diff[1];

	if (i_rpeaks < 9 && i_squar < buffer_lenght ){
		squar[i_squar] =  ddiff*ddiff; 
		i_squar++;
		i_rpeaks++;
		///rotate square buffer
		shift_left_array(buffer_ECG,NULL,sizeof(buffer_ECG));
		return 0;
	}
	else{
		
		squar[buffer_lenght - 1] =   ddiff * ddiff; 
		processed_ecg = (squar[0]+squar[1]+squar[2]+squar[3]+squar[4])/5;
		shift_left_array(buffer_ECG,squar,sizeof(squar));
	}
	
	switch (state){
		
		case 1: 
      
				if (counter < tf1){
						if (processed_ecg > Rpeakamp){   
							Rpeakamp = processed_ecg;
							rpeakpos = i_rpeaks;
						}
					}
				else {
          Ramptotal = ((aaa*Ramptotal ) + (bbb*Rpeakamp));
					//setting time for state 2
					d = (i_rpeaks - rpeakpos);
					tf2 = (tf1 + (50 - d));
					threshold = Ramptotal   ; 
					i_rpeaks++;
					counter++;
          state = 2;
					if (last_peak == 0) {
						last_peak = rpeakpos - ND + 2; 
					}
					else {
					}
					return (rpeakpos - ND + 2); 
				}
			break;
		
		case 2:
				if (counter > tf2){
						state = 3;	
					}
			break;
			
		case 3 :
			if (processed_ecg < threshold){
					threshold = threshold*expon;
			}
			else {
				counter = 0;
				state = 1;
				Rpeakamp = 0;
      }
			break;
		default :
			break;
	}
	counter++;
	i_rpeaks++;
	return 0;		
}
  

// HEART RATE from RR-INTERVALS 
void swap(uint16_t *p,uint16_t *q) {
   uint16_t t;   // temporary value
   t = *p;
   *p = *q;
   *q = t;
}

// sort array
void sort(uint16_t a[],uint16_t n) {
   uint8_t i,j;
   for(i = 0; i < n-1; i++) {
      for(j = 0; j < n-i-1; j++) {
         if(a[j] > a[j+1])
            swap(&a[j],&a[j+1]);
      }
   }
}

void heartrate_new(heartrateStruct *heartrateStruct_var){
			const uint8_t median_length = 15;
			static uint16_t last_rr[median_length];
			static uint32_t last_peak = 0;
			static uint16_t ordered[median_length];
			static uint16_t hr;
				
			// first detected peak
			if (last_peak == 0) {
						last_peak = heartrateStruct_var->rpeaks;
						heartrateStruct_var->heartrate = 0;
						heartrateStruct_var->rr_intervals = 0;
				}
				
			else {	 
					// rotate RR-intervals buffer
					for (int j = 0; j < median_length - 1; j++)
					{
						last_rr[j] = last_rr[j+1];
					}

					// add detected peak
					last_rr[median_length - 1] = 1000 * (heartrateStruct_var->rpeaks - last_peak) / (freq_sample);
					
					// median of the RR-intervals vector
					for(int loop = 0; loop < median_length - 1 ; loop++) {
						ordered[loop] = last_rr[loop];
					}
					sort(ordered,median_length);
								
					
					// if the buffer is not filled yet or transient of the ECG	(4000 samples)				 
					if (last_rr[0] == 0  || heartrateStruct_var->rpeaks < 4000) {
							heartrateStruct_var->heartrate = 0;				
							heartrateStruct_var->rr_intervals = 0;
						}
					else
						{
							// compute heartrate at each detected rpeak from RR-intervals median
							hr = (double)(1000 * 60) / ordered[median_length / 2];
							if (hr < 40 || hr > 200){
								hr = 0;
							}
							heartrateStruct_var-> heartrate = hr;
							
							// replace RR-intervals that differ 30% from the RR-intervals median
							if(last_rr[median_length - 1] < 0.7 * ordered[ median_length / 2] || last_rr[median_length - 1] > 1.3 * ordered[median_length / 2]) {
								heartrateStruct_var->rr_intervals = ordered[ median_length / 2];		
							}
							else 
							{
								heartrateStruct_var->rr_intervals = last_rr[median_length - 1];
							}
						}
					last_peak = heartrateStruct_var->rpeaks;						
				}
}


// sample by sample FIR filter
int16_t fir_filt_circ_buff(int16_t x) {
	
	// FIR filter 3-45 Hz, (MATLAB) b = fir1(108,[3 45]/(250/2));
	#define NUM_TAPS 109
	double firCoeffs[NUM_TAPS] = {
		-8.50784869513188e-05,	0.000244855135717125,	0.000748202810178776,	0.000841137485699446,	0.000345171011837738,	-0.000244548258690259,	-0.000221781532121603,	0.000509008777032962,	
		0.00116072880672235,	0.000836579626683436,	-0.000344859099569471,	-0.00113453494925602,	-0.000486891944780731,	0.00100982717866958,	0.00147155444969213,	-0.000148062192709959,	
		-0.00247881339822322,	-0.00293298410976999,	-0.000790928713939187,	0.00142123486839599,	0.000461999675794594,	-0.00359668337382620,	-0.00674318856733038,	-0.00534673260554557,	
		-0.000890580831739072,	0.000884831056100501,	-0.00354642950909424,	-0.0105777317109142,	-0.0126753696522936,	-0.00717352371394026,	-0.000548300522134229, -0.00192964848772887,	
		-0.0120816283000055,	-0.0209162854700595,	-0.0181967516457359,	-0.00635083409310265,	0.000282184435763781,	-0.00874906288160041,	-0.0261941462532903,	-0.0328562009064390,
		-0.0193350012656816,	0.000293571158493586,	0.00137154191630452,	-0.0226574062353388,	-0.0480417868261260,	-0.0434772257127053,	-0.00752328862464773,	0.0215996401679703,	
		0.00229853460542648,	-0.0595783906356175,	-0.100373769230414,	-0.0497478978216415,	0.0982487197088897,	0.263387447391793,	0.335433028930619,	0.263387447391793,	0.0982487197088897,	
		-0.0497478978216415,	-0.100373769230414,	-0.0595783906356175,	0.00229853460542648,	0.0215996401679703,	-0.00752328862464773,	-0.0434772257127053,	-0.0480417868261260,	-0.0226574062353388,	
		0.00137154191630452,	0.000293571158493586,	-0.0193350012656816,	-0.0328562009064390,	-0.0261941462532903,	-0.00874906288160041,	0.000282184435763781,	-0.00635083409310265,	
		-0.0181967516457359,	-0.0209162854700595,	-0.0120816283000055,	-0.00192964848772887,	-0.000548300522134229,	-0.00717352371394026,	-0.0126753696522936,	-0.0105777317109142,	
		-0.00354642950909424,	0.000884831056100501,	-0.000890580831739072,	-0.00534673260554557,	-0.00674318856733038,	-0.00359668337382620,	0.000461999675794594,	0.00142123486839599,	
		-0.000790928713939187,	-0.00293298410976999,	-0.00247881339822322,	-0.000148062192709959, 0.00147155444969213,	0.00100982717866958,	-0.000486891944780731, -0.00113453494925602,	
		-0.000344859099569471,	0.000836579626683436,	0.00116072880672235,	0.000509008777032962,	-0.000221781532121603,	-0.000244548258690259, 0.000345171011837738,	0.000841137485699446,	
		0.000748202810178776,	0.000244855135717125,	-8.50784869513188e-05};
		static int16_t p = 0;
		static int16_t z[NUM_TAPS];
		double y = 0;
		
		// circular buffer for input signal x
		p = p + 1;
		if (p > NUM_TAPS){
			p = 1;
		}
		z[p - 1] = x;
		int16_t k = p; // index for the signal x buffer position
		for (int j = 0; j < NUM_TAPS - 1; j++)   
						{
							y = (double) y + firCoeffs[j]*z[k]; // convolution input signal and FIR coefs
							k = k - 1;
							if (k < 0) {
								k = NUM_TAPS - 1;
							}
						}
		return y;
	}

