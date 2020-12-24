FROM gradle:6.7.1-jdk11

COPY . /app
RUN chown -R gradle /app
WORKDIR /app
RUN apt-get update && apt-get install -y libfuse-dev
RUN ["./gradlew", "fsJar"]
RUN ["./gradlew", "jar"]
ENTRYPOINT ["./run.sh"]
