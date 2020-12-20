using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using CarpetRadar.Services.Models;
using Cassandra;
using NLog;

namespace CarpetRadar.Services.DataStorage
{
    public interface IDataStorage
    {
        Task<string> AddFlightState(FlightState flightState, Guid userId);

        Task<IEnumerable<CurrentPosition>> GetCurrentPositions();

        Task<IEnumerable<Flight>> GetUserFlights(Guid userId);

        Task<IEnumerable<(Guid Id, string Login, string Company)>> GetUserInfos();

        Task<(string Login, string Company)> GetUserInfo(Guid userId);

        Task SaveUserInfo(string login, Guid userId, long passwordHash, string company);

        Task<(Guid UserId, long Hash)?> GetUserIdAndPasswordHash(string login);

        Task SetUserToken(Guid userId, string token);

        Task<(Guid?, DateTime?)> FindUser(string token);
    }

    public class DataStorage : IDataStorage
    {
        private readonly ISession session;
        private readonly ILogger logger;

        internal DataStorage(ISession session, ILogger logger)
        {
            this.session = session;
            this.logger = logger;

            /// try prepared statements
            /// try sql injection
        }

        public async Task<string> AddFlightState(FlightState flightState, Guid userId)
        {
            if (string.IsNullOrEmpty(flightState.Label)
                || string.IsNullOrEmpty(flightState.License)
                || flightState.FlightId == Guid.Empty
                || flightState.X < 0
                || flightState.Y < 0)
                return "Empty request parameters";

            var c = $"UPDATE {Constants.ColumnFamily.CarpetFlights} SET " +
                    $"user_id = {userId}, " +
                    $"label = '{flightState.Label}', " +
                    $"license = '{flightState.License}', " +
                    $"finished = {flightState.Finished}, " +
                    $"x = x + [{flightState.X}], " +
                    $"y = y + [{flightState.Y}], " +
                    $"time = time + [{DateTimeOffset.UtcNow.ToUnixTimeMilliseconds()}] " +
                    $"WHERE id = {flightState.FlightId};";
            var addToCarpets = new SimpleStatement(c);

            var addToPositions = new SimpleStatement(
                $"INSERT INTO {Constants.ColumnFamily.CurrentPositions} (user_id, id, label, x, y, finished) VALUES (?, ?, ?, ?, ?, ?)",
                userId, flightState.FlightId, flightState.Label, flightState.X, flightState.Y, flightState.Finished);
            await session.ExecuteAsync(new BatchStatement()
                .Add(addToCarpets)
                .Add(addToPositions));
            return null;
        }

        public async Task<IEnumerable<CurrentPosition>> GetCurrentPositions()
        {
            /// нужно чистить curPos
            var statement = new SimpleStatement(
                $"SELECT * FROM {Constants.ColumnFamily.CurrentPositions}");
            statement.SetPageSize(100);
            var rs = session.Execute(statement);
            var coordinates = rs.Select(row =>
                new CurrentPosition
                {
                    UserId = row.GetValue<Guid>("user_id"),
                    FlightId = row.GetValue<Guid>("id"),
                    Label = row.GetValue<string>("label"),
                    X = row.GetValue<int>("x"),
                    Y = row.GetValue<int>("y"),
                    Finished = row.GetValue<bool>("finished"),
                });
            return coordinates;
        }

        public async Task<IEnumerable<Flight>> GetUserFlights(Guid userId)
        {
            var statement = new SimpleStatement(
                $"SELECT * FROM {Constants.ColumnFamily.CarpetFlights} WHERE user_id = {userId} ALLOW FILTERING;"); ///
            statement.SetPageSize(100);
            var rs = session.Execute(statement);
            var coordinates = rs.Select(row =>
                new Flight
                {
                    FlightId = row.GetValue<Guid>("id"),
                    Label = row.GetValue<string>("label"),
                    License = row.GetValue<string>("license"),
                    X = row.GetValue<List<int>>("x"),
                    Y = row.GetValue<List<int>>("y"),
                    ReportMoments = row.GetValue<List<DateTimeOffset>>("time").Select(time => time.UtcDateTime).ToList(),
                    Finished = row.GetValue<bool>("finished")
                });
            return coordinates;
        }

        public async Task<IEnumerable<(Guid Id, string Login, string Company)>> GetUserInfos()
        {
            var statement = new SimpleStatement(
                $"SELECT id, login, company FROM {Constants.ColumnFamily.Users}");
            statement.SetPageSize(100);
            var rs = session.Execute(statement);
            var users = rs.Select(row => (
                Id: row.GetValue<Guid>("id"),
                Login: row.GetValue<string>("login"),
                Company: row.GetValue<string>("company")));
            return users;
        }

        public async Task<(string Login, string Company)> GetUserInfo(Guid userId)
        {
            var statement = new SimpleStatement(
                $"SELECT login, company FROM {Constants.ColumnFamily.Users} WHERE id = {userId} ALLOW FILTERING;");
            var rs = session.Execute(statement);

            var userData = rs.FirstOrDefault();

            return (Login: userData?.GetValue<string>("login"),
                Company: userData?.GetValue<string>("company"));
        }

        public async Task SaveUserInfo(string login, Guid userId, long passwordHash, string company)
        {
            var statement = new SimpleStatement(
                $"UPDATE {Constants.ColumnFamily.Users} SET " +
                $"id = {userId}, " +
                $"password_hash = {passwordHash}, " +
                $"company = '{company}' " +
                $"WHERE login = '{login}';");
            session.Execute(statement);
        }

        public async Task<(Guid UserId, long Hash)?> GetUserIdAndPasswordHash(string login)
        {
            var statement = new SimpleStatement(
                $"SELECT id, password_hash FROM {Constants.ColumnFamily.Users} " +
                $"WHERE login = '{login}'");
            var rs = session.Execute(statement);
            var userData = rs.FirstOrDefault();
            if (userData == null)
                return null;
            return (UserId: userData.GetValue<Guid>("id"),
                Hash: userData.GetValue<long>("password_hash"));
        }

        public async Task SetUserToken(Guid userId, string token)
        {
            var statement = new SimpleStatement(
                $"UPDATE {Constants.ColumnFamily.Tokens} SET " +
                $"user_id = {userId}, " +
                $"time = {DateTimeOffset.UtcNow.ToUnixTimeMilliseconds()} " +
                $"WHERE token_ = '{token}';");

            session.Execute(statement);
        }

        public async Task<(Guid?, DateTime?)> FindUser(string token)
        {
            var statement = new SimpleStatement(
                $"SELECT user_id, time FROM {Constants.ColumnFamily.Tokens} " +
                $"WHERE token_ = '{token}';");
            var rs = session.Execute(statement);
            var userTokenData = rs.FirstOrDefault();
            var userId = userTokenData?.GetValue<Guid>("user_id");
            var authTime = userTokenData?.GetValue<DateTimeOffset>("time").UtcDateTime;
            return (userId, authTime);
        }
    }
}
