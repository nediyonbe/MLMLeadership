# Leadership-Simulator for Multilevel Marketing
This program enables the calculation of compensation for members of a multilevel marketing company.
While there exist several companies all with their own terminology, they are all based on the simple idea of people having teams; members in their teams having further teams and so on. This concept is mostly explained via terms such as "generation" and "level" again, depending on company terminology. Everyone is positioned in a generation X with respect to a person where X is the numbe rof people in between along a "leg". This generaiton concept is widely used in criteria as well as compensation calculations. Another term required to know is sponsor: If person A is in team of B; B is A's sponsor

People satisfying different criteria qualify for different degrees / levels / titles. While the criteria can vary, the following ones are covered in this program as they are the most common ones:
1. Number of people placing an order in your team
2. Total order of people placing an order in your X number of generations
3. Total number of people that joined your team
4. Number of people with title X in your generation 1

Among the 4 criteria above, the 4th one is critical as it imposes generation by generation calculation across the whole client set. In a market of 20K people dispersed across 10 generations that is not a practical task to do via a spreadsheet

Based on the above criteria, the compensation is calculated for every person. Compensation is mostly based on the generation as well. The orders coming from different generaitons are multiplied with varying multipliers, generation 1 orders having a higher compared to 2; 2 to 3 and so on in general

To avoid double payment especially for clients with higher titles, some companies exclude team members above a certain title. That feautre is also available here

![](2019-05-30-17-09-10.png)

## Installation
Use Python along with the following modules: pandas / math / numpy / ctypes / time / ttk / matplotlib

Among these ttk provides with the user interface to enter parameters for the aforementioned criteria so that the user can test different scenarios. Matplotlib depicts the results via barcharts

## Usage
The main use case considered is a company having actual data of clients with their info on sales and each client's sponsor

Through the interface the user enters parameters, browses for the input data file. The program calculates information such as generation with respect to the highest person in the leg, the sales in generation 1-2-3 of every person, the number of people placing an order in every person's generation 1-2-3. Due to the 4th criteria above, all calculations are done generation by generation, starting with the deepest. That way titles are calculated in the deepest generation thereby enabling the calculation of titles in one level higher and so on.

The results are exported as a csv file and also presented as bar charts. If the actual compensations are also given, the charts show a comparison of the alternative scenario and the actual

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License
MIT