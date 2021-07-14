ARG BASE_IMAGE=opensciencegrid/software-base:3.5-el7-release
FROM ${BASE_IMAGE}
ARG BASE_IMAGE

LABEL org.opencontainers.image.title="HTCondor ATLAS AF Execute image derived from ${BASE_IMAGE}"

RUN yum install -y \
  @development \
  jq \ 
  zsh \
  tcsh \
  git \ 
  bc \
  bind-utils \
  cpio \
  ed \
  file \
  bzip2 \ 
  gnupg2 \
  libaio \
  rdate \ 
  rng-tools \ 
  rsync \ 
  tcsh \ 
  time \ 
  wget \
  which \ 
  words \ 
  xz \ 
  zip \
  yum-utils \ 
  dos2unix

RUN yum install --enablerepo=osg-upcoming -y condor

RUN yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
RUN yum install -y docker-ce-cli

COPY condor/*.conf /etc/condor/config.d/
COPY cron/* /etc/cron.d/
COPY supervisor/* /etc/supervisord.d/
COPY image-config/60-user.sh /etc/osg/image-config.d/60-user.sh
