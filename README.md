# Cifer

😋 Meet `Cifer`, the blockchain data little wizard, 
stealthily crawling through the web with the agility of a producer-consumer pattern, 
all while keeping it asynchronous for that extra oomph!

> Tip: 基于生产者-消费者的异步区块链数据爬取！

## ✅ Get Ready?

Before you start, enter the following command in the virtual environment.

```
pip install -r requirements.txt
```

## 🔰 Get Started





Command Line Mode


Function Call Mode



## 🎉 PCP Power-Up

In the Producer-Consumer Pattern, the main entities involved include: 
Producer (`Pro`), Consumer (`Con`), `Job`, `Task`, Source Queue (`SQ`), and Job Queue (`JQ`). 
The responsibilities of each entity are as follows:

- `Task`: The fundamental unit of execution for the crawler.
- `Job`: Coordinates the asynchronous execution of multiple `Tasks`.
- `SQ`: Holds `Jobs` pending assignment.
- `JQ`: Contains `Jobs` ready for processing.
- `Pro`: Loads `Jobs` from the `SQ` into the `JQ`. 
- `Con`: Pulls and completes `Jobs` from the `JQ`.

Under this pattern, 
the main program first consolidates multiple `Tasks` that are related in business logic into a single `Job` 
and then stores it in the `SQ`. After that, the `Pro` takes the pending `Jobs` from the `SQ`
and places them into the `JQ`. Subsequently, multiple `Cons`, based on network conditions, 
asynchronously retrieve and execute these ready `Jobs` from the `JQ`, 
ultimately completing the data crawling process.




