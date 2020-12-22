FROM gradle:6.7.1-jdk11

COPY . /app
RUN chown -R gradle /app
WORKDIR /app
RUN ["./gradlew", "jar"]
ENTRYPOINT ["java", "-jar", "./build/libs/keeper-1.0-SNAPSHOT.jar"]
