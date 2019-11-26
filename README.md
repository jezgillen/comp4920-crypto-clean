# Coinye

Desktop app for analysing and visualising the performance of simple trading algorithms.



## Authors

* [wandy0394](https://github.com/wandy0394)

* [mehri-amin](https://github.com/mehri-amin)

* [JulianJankowski](https://github.com/JulianJankowski)

* [HarryW102](https://github.com/HarryW102)

* [jezgillen](https://github.com/jezgillen)



## Linux & macOS

To install requirements, run 

```
pip3 install -r requirements.txt
```

To run the program

```
python3 coinye.py
```



## Windows

Haven't got it working on the CSE Windows machines, due to some problem with importing PyQt5.

However, it does work fine on other Windows machines.



## Troubleshooting

On the CSE computers, you may have the following error:

 "<urlopen error [SSL: CERTIFICATE_VERIFY_FAILED]"

If you face this problem, uncomment the two lines 369 and 370 in coinye.py

Then it should work 
