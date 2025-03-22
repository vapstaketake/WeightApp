#include <iostream>
#include <wiringPi.h>

double readHx711Count(int GpioPinDT = 2, int GpioPinSCK = 3) {

    wiringPiSetupGpio(); // Initialize wiringPi to use GPIO pin numbers (not WiringPi numbers)
    // e.g. 22 = GPIO 22 = Wiring Pi Pin 3 = Physical Pin 15

    int i;
    unsigned int Count = 0;
    pinMode(GpioPinDT, OUTPUT);
    digitalWrite(GpioPinDT, HIGH);
    pinMode(GpioPinSCK, OUTPUT); // [Edit] did not do this originally but after reboot it was reset and stopped it working
    digitalWrite(GpioPinSCK, LOW);
    pinMode(GpioPinDT, INPUT);
    while (digitalRead(GpioPinDT) == 1) {
        i = 0;
    }
    for (i = 0; i < 24; i++) {
        digitalWrite(GpioPinSCK, HIGH);
        Count = Count << 1;
        
        digitalWrite(GpioPinSCK, LOW);
        if (digitalRead(GpioPinDT) == 0) {
            Count = Count + 1;
        }
    }
    digitalWrite(GpioPinSCK, HIGH);
    Count = Count ^ 0x800000;
    digitalWrite(GpioPinSCK, LOW);
    return double (Count);
}


int main() {

    auto offset = 8156931; // Run with 0 initially to get the average
    auto actualWeight = 300.0; // Initially make 1 for calibration
    auto measuredWeight = 113318.0; // Initially make 1 for calibration
    auto factor = actualWeight / measuredWeight; 
    auto average = 0;
    auto MaxMeasurements = 10;
    for (auto measure = 1; measure <= MaxMeasurements; measure++) {
        auto reading = readHx711Count();
        average += reading;
        std::cout << measure << "\tMeasure\t" << reading  << "\tWeight\t" << (reading-offset) * factor << std::endl;
        delay(50);
    }
    average /= MaxMeasurements;
    std::cout << "Average" << "\tMeasure\t" << average  << "\tWeight\t" << (average-offset) * factor << std::endl;

    return 0;
}
