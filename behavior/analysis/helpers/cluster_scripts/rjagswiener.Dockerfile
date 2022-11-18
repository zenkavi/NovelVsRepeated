FROM rocker/tidyverse:4

RUN apt-get update && apt-get install -y wget

RUN wget https://sourceforge.net/projects/mcmc-jags/files/JAGS/4.x/Source/JAGS-4.3.1.tar.gz \
  && tar -xf JAGS-4.3.1.tar.gz \
  && cd JAGS-4.3.1 \
  && ./configure && make && make install \
  && cd / \
  && wget https://sourceforge.net/projects/jags-wiener/files/JAGS-WIENER-MODULE-1.1.tar.gz \
  && tar -xf JAGS-WIENER-MODULE-1.1.tar.gz \
  && cd JAGS-WIENER-MODULE-1.1 \
  && ./configure && make && make install \
  && install2.r runjags here optparse
