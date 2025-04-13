#include <iostream>
#include <wiringPi.h>

double readHx711Count(int GpioPinDT = 2, int GpioPinSCK = 3) {
    wiringPiSetupGpio();
    
    int i;
    unsigned int Count = 0;
    pinMode(GpioPinDT, OUTPUT);
    digitalWrite(GpioPinDT, HIGH);
    pinMode(GpioPinSCK, OUTPUT);
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
    return double(Count);
}

int main() {
    double reading = readHx711Count();
    std::cout << reading << std::endl;
    return 0;
}
