using System;
using Cassandra;
using NLog;

namespace CarpetRadar.Services.DataStorage
{
    public static class DataStorageBuilder
    {
        private static ICluster cluster;
        private static ISession session;
        private static readonly object Lock = new object();

        public static DataStorage GetDefaultStorage(ILogger logger)
        {
            lock (Lock)
            {
                try
                {
                    if (cluster != null)
                        return new DataStorage(session, logger);

                    cluster = Cluster.Builder()
                        .AddContactPoint("localhost")
                        .WithPort(9042)
                        .WithLoadBalancingPolicy(new DCAwareRoundRobinPolicy("datacenter1"))
                        .WithAuthProvider(new PlainTextAuthProvider("cassandra", "cassandra"))
                        .Build();

                    session = cluster.Connect();
                    CreateKeySpace();
                    session.ChangeKeyspace(Constants.KeySpace);
                    logger.Info("The cluster's name is: " + cluster.Metadata.ClusterName);

                    CreateTables();

                    return new DataStorage(session, logger);
                }
                catch (Exception e)
                {
                    logger.Error(e);
                    throw;
                }
            }
        }

        private static void CreateKeySpace()
        {
            var createKeySpace = new SimpleStatement($"CREATE KEYSPACE IF NOT EXISTS {Constants.KeySpace} " +
                                                     "WITH replication = { " +
                                                     "'class':'SimpleStrategy', " +
                                                     "'replication_factor' : 3};");
            session.Execute(createKeySpace);
        }

        private static void CreateTables()
        {
            var createUsers = new SimpleStatement(
                $"CREATE COLUMNFAMILY IF NOT EXISTS {Constants.ColumnFamily.Users}(" +
                "login text, " +
                "id uuid, " +
                "password_hash bigint, " +
                "company text, " +
                "PRIMARY KEY(login));");

            var createTokens = new SimpleStatement(
                $"CREATE COLUMNFAMILY IF NOT EXISTS {Constants.ColumnFamily.Tokens}(" +
                "token_ ascii, " +
                "user_id uuid, " +
                "time timestamp, " +
                "PRIMARY KEY(token_));");

            var createFlights = new SimpleStatement(
                $"CREATE COLUMNFAMILY IF NOT EXISTS {Constants.ColumnFamily.CarpetFlights}" +
                "(id uuid, " +
                "user_id uuid, " +
                "label ascii, " +
                "license ascii, " +
                "time list<timestamp>, " +
                "x list<int>, " +
                "y list<int>, " +
                "finished boolean, " +
                "PRIMARY KEY(id));");

            var createCurrentPositions = new SimpleStatement(
                $"CREATE COLUMNFAMILY IF NOT EXISTS {Constants.ColumnFamily.CurrentPositions}(" +
                "id uuid, " +
                "user_id uuid, " +
                "label text, " +
                "x int, " +
                "y int, " +
                "finished boolean, " +
                "PRIMARY KEY(id));");

            session.Execute(createUsers);
            session.Execute(createTokens);
            session.Execute(createFlights);
            session.Execute(createCurrentPositions);
        }
    }
}
