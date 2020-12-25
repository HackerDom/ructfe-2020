using System;
using System.IO;
using System.Linq;
using System.Net;
using System.Net.Sockets;
using System.Runtime.Serialization.Formatters.Binary;
using System.Threading;
using CarpetRadar.Services;
using CarpetRadar.Services.DataStorage;
using CarpetRadar.Services.IdentityServices;
using CarpetRadar.Services.Models;
using NLog;

namespace CarpetRadar.TrackServer
{
    public class CarpetTracker
    {
        private readonly TcpListener server;

        private readonly ILogger logger;
        private readonly IDataStorage dataStorage;
        private readonly IAuthenticationService authService;

        public CarpetTracker(string ip, int port)
        {
            var localAddress = IPAddress.Parse(ip);

            logger = LogManager.GetCurrentClassLogger();
            dataStorage = DataStorageBuilder.GetDefaultStorage(logger);
            authService = new AuthenticationService(dataStorage);

            server = new TcpListener(localAddress, port);
            server.Start();
            StartListener();

            ThreadPool.GetMaxThreads(out var workerThreads, out var completionPortThreads);
            logger.Info($"Threadpool characteristics: maxThreadsNumber={workerThreads}, maxIOThreadsNumber={completionPortThreads}");
        }

        public void StartListener()
        {
            try
            {
                while (true)
                {
                    ThreadPool.GetAvailableThreads(out var workerThreads, out var completionPortThreads);
                    logger.Info($"Threadpool characteristics: available={workerThreads}, availableIO={completionPortThreads}");

                    var client = server.AcceptTcpClient();
                    logger.Info($"Connected: {client.Client.RemoteEndPoint.Serialize()}");

                    ThreadPool.QueueUserWorkItem(HandleDevice, client);
                }
            }
            catch (SocketException e)
            {
                logger.Warn(e, "SocketException");
                server.Stop();
            }
        }

        private async void HandleDevice(object obj)
        {
            var client = (TcpClient) obj;
            var stream = client.GetStream();
            try
            {
                var bf = new BinaryFormatter();
                var request = (FlightState) bf.Deserialize(stream);

                var userId = await authService.ResolveUser(request.Token);
                if (userId == null)
                {
                    stream.Send("Authentication error.");
                    return;
                }

                var errorMsg = await dataStorage.AddFlightState(request, userId.Value);
                if (errorMsg != null)
                {
                    stream.Send(errorMsg);
                    return;
                }

                var currentPositions = (await dataStorage.GetCurrentPositions()).ToArray();

                using (var ms = new MemoryStream())
                {
                    bf.Serialize(ms, currentPositions);
                    var array = ms.ToArray();
                    stream.Write(array, 0, array.Length);
                }
            }
            catch (Exception e)
            {
                logger.Warn(e, "Exception");
                logger.Warn(e.Message);
                logger.Warn(e.StackTrace);
                stream.TrySend("Internal error");
            }
            finally
            {
                client.Close();
            }
        }
    }
}
