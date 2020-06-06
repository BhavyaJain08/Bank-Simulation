"""
Created on 04/222/2020
by Bhavya jain
"""
import numpy as np
import pandas as pd

class Bank_Simulation:
    def __init__(self): 
        self.clock=0.0                      #simulation clock
        self.num_arrivals=0                 #total number of arrivals
        self.t_arrival=self.gen_int_arr()   #time of next arrival
        self.t_departure1=float('inf')      #departure time from server 1
        self.t_departure2=float('inf')      #departure time from server 2
        self.dep_sum1=0                     #Sum of service times by teller 1
        self.dep_sum2=0                     #Sum of service times by teller 2
        self.state_T1=0                     #current state of server1 (binary)
        self.state_T2=0                     #current state of server2 (binary)
        self.total_wait_time=0.0            #total wait time
        self.num_in_q=0                     #current number in queue
        self.number_in_queue=0              #customers who had to wait in line(counter)
        self.num_in_system=0                #current number of customers in system
        self.num_of_departures1=0           #number of customers served by teller 1  
        self.num_of_departures2=0           #number of customers served by teller 2 
        self.lost_customers=0               #customers who left without service
        
    def time_adv(self):                                                       #timing routine
        t_next_event=min(self.t_arrival,self.t_departure1,self.t_departure2)  #determine time of next event
        self.total_wait_time += (self.num_in_q*(t_next_event-self.clock))
        self.clock=t_next_event
                
        if self.t_arrival<self.t_departure1 and self.t_arrival<self.t_departure2:
            self.arrival()
        elif self.t_departure1<self.t_arrival and self.t_departure1<self.t_departure2:
            self.teller1()
        else:
            self.teller2()
            
        
    
    def arrival(self):              
        self.num_arrivals += 1
        self.num_in_system += 1

        if self.num_in_q == 0:                              #schedule next departure or arrival depending on state of servers
            if self.state_T1==1 and self.state_T2==1:
                self.num_in_q+=1
                self.number_in_queue+=1
                self.t_arrival=self.clock+self.gen_int_arr()
                
                
            elif self.state_T1==0 and self.state_T2==0:
                
                if np.random.choice([0,1])==1:
                    self.state_T1=1
                    self.dep1= self.gen_service_time_teller1()
                    self.dep_sum1 += self.dep1
                    self.t_departure1=self.clock + self.dep1
                    self.t_arrival=self.clock+self.gen_int_arr()

                else:
                    self.state_T2=1
                    self.dep2= self.gen_service_time_teller2()
                    self.dep_sum2 += self.dep2
                    self.t_departure2=self.clock + self.dep2
                    self.t_arrival=self.clock+self.gen_int_arr()

                    
            elif self.state_T1==0 and self.state_T2 ==1:    #if server 2 is busy customer goes to server 1
                self.dep1= self.gen_service_time_teller1()
                self.dep_sum1 += self.dep1
                self.t_departure1=self.clock + self.dep1
                self.t_arrival=self.clock+self.gen_int_arr()
                self.state_T1=1
            else:                                           #otherwise customer goes to server 2
                self.dep2= self.gen_service_time_teller2()
                self.dep_sum2 += self.dep2
                self.t_departure2=self.clock + self.dep2
                self.t_arrival=self.clock+self.gen_int_arr()
                self.state_T2=1
        
        elif self.num_in_q < 4 and self.num_in_q >= 1:
            self.num_in_q+=1
            self.number_in_queue+=1                             #if queue length is less than 4 generate next arrival and make customer join queue
            self.t_arrival=self.clock + self.gen_int_arr()
            
        elif self.num_in_q == 4:                             #if queue length is 4 equal prob to leave or stay
            if np.random.choice([0,1])==0: 
                self.num_in_q+=1 
                self.number_in_queue+=1                 
                self.t_arrival=self.clock + self.gen_int_arr()
            else:
                self.lost_customers+=1
                
                
        elif self.num_in_q >= 5:                            #if queue length is more than 5 60% chance of leaving
            if np.random.choice([0,1],p=[0.4,0.6])==0:
                self.t_arrival=self.clock+self.gen_int_arr()
                self.num_in_q+=1 
                self.number_in_queue+=1 
            else:
                self.lost_customers+=1
                
            

    
    def teller1(self):              #departure from server 2
        self.num_of_departures1 += 1
        self.num_in_system -= 1 
        if self.num_in_q>0:
            self.dep1= self.gen_service_time_teller1()
            self.dep_sum1 += self.dep1
            self.t_departure1=self.clock + self.dep1
            self.num_in_q-=1
        else:
            self.t_departure1=float('inf') 
            self.state_T1=0                  
    
    def teller2(self):              #departure from server 1
        self.num_of_departures2 += 1
        self.num_in_system -= 1
        if self.num_in_q>0:
            self.dep2= self.gen_service_time_teller2()
            self.dep_sum2 += self.dep2
            self.t_departure2=self.clock + self.dep2
            self.num_in_q-=1
        else:
            self.t_departure2=float('inf')
            self.state_T2=0
            
    
    def gen_int_arr(self):                                             #function to generate arrival times using inverse trnasform
        return (-np.log(1-(np.random.uniform(low=0.0,high=1.0))) * 3)
    
    def gen_service_time_teller1(self):                                #function to generate service time for teller 1 using inverse trnasform
        return (-np.log(1-(np.random.uniform(low=0.0,high=1.0))) * 1.2)
    
    def gen_service_time_teller2(self):                                #function to generate service time for teller 1 using inverse trnasform
        return (-np.log(1-(np.random.uniform(low=0.0,high=1.0))) * 1.5)


   
s=Bank_Simulation()
df=pd.DataFrame(columns=['Average interarrival time','Average service time teller1','Average service time teller 2','Utilization teller 1','Utilization teller 2','People who had to wait in line','Total average wait time','Lost Customers'])


for i in range(100):
    np.random.seed(i)
    s.__init__()
    while s.clock <= 240 :
        s.time_adv() 
    a=pd.Series([s.clock/s.num_arrivals,s.dep_sum1/s.num_of_departures1,s.dep_sum2/s.num_of_departures2,s.dep_sum1/s.clock,s.dep_sum2/s.clock,s.number_in_queue,s.total_wait_time,s.lost_customers],index=df.columns)
    df=df.append(a,ignore_index=True)   
    
df.to_excel('results.xlsx')    



    