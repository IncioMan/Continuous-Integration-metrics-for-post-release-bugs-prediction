This repository contains the code developed during the Msc. Thesis project carried out at the [Technical University of Denmark](https://www.dtu.dk/) as completion of the Master degree in the [Computer Science and Engineering](https://www.dtu.dk/english/education/msc/programmes/computer_science_and_engineering) study line.

## Title
Using Continuous Integration
metrics to predict post-release
bugs

### Problem statement
The popularity and adoption of software products have increased drastically in
the last decades. Software applications are employed in many different fields,
ranging from entertainment to critical applications. Software systems have also
experienced an increase in complexity, which allowed them to become more
powerful and keep up with the market requirements. These products are usually
developed under various constraints, such as time, resource or budget,
and this aspect represents a challenge when it comes to assess the quality of the
product and deliver fault free software. Indeed, requirements and constraints may vary from one field to another, but one common ambition is to develop
software products with no faults. Faults, or bugs, are intended as deviations
from the expected behavior or the desired functionality, and software companies
are interested in detecting faults in the code as soon as possible, possibly before
the code is released to customers. The early detection of a bug helps solve it
faster, before it is deployed in production and before other software components
rely on that functionality, allowing to limit its consequences. Depending on
the field, a bug reaching the end-user may simply affect the user-experience,
e.g. in case of entertainment, or cause serious damage, in case of safety critical
scenarios.
For these reasons it is important to develop solutions that can support the
decision of whether or not the software is faulty or ready to be released, by
exploiting data produced during its development.

### Conclusions
This research aimed to evaluate whether Continuous Integration execution data
could represent a valid source of information to help predict the quality of a software
release. Based on the results collected from the analysis of the constructed
datasets, it can be conclude that this type of metrics does provide informative
contributions with regards to the prediction of the number of post-release bugs
in software releases. Although we observed unstable or biased predictions in the
regression tasks, in binary classification models performed acceptably, reaching
up to a median of 87% accuracy.
Our approach provides several benefits. Firstly, it allows to exploit often unused
data produced and stored on the CI server. Secondly, it adds a new possible
type of data to be used in the field of bug prediction, which is a complex task
and can benefit from a large plethora of metrics to allow to find the best suited
combination for each project. Lastly, using these CI metrics allows to identify
common CI related traits of releases with similar number of bugs, and therefore
provide guidance in what practices to improve.
The experiments carried out suggest that the proposed metrics are more informative
when collected from a relative homogeneous (configuration and build
tools wise) Continuous Integration period. This result can be of great value to
those interested in utilizing CI metrics for release quality prediction, as they
can limit data collection and extraction only to releases developed using similar Continuous Integration settings. On the other hand, this poses a limitation to
the quantity of valid data available: given that the CI process may evolve over
time, it may be necessary to release a certain amount of versions before having
enough training data.

## Repository structre
* Jupyter Notebooks are stored in this [folder](/notebooks)
    * In this [subfolder](/notebooks/analysis/) are stored the ones containing the analysis of the various datasets
    * In this [subfolder](notebooks/parser_and_validation/) are stored the ones containing the parsing and validation of the raw datasets
* Scripts for retrieving data from the data sources are stored in this [folder](data_retrivers)
* Datasets are stored in csv format and can be found in this [subfolder](/csv)
    * The final datasets for the final analysis/comparison/prediction are stored in this [folder](csv/final_datasets)
