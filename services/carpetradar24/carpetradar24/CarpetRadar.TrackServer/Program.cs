using CarpetRadar.Services.Models;
using System;
using System.IO;
using System.Runtime.Serialization.Formatters.Binary;

namespace CarpetRadar.TrackServer
{
    class Program
    {
        static void Main()
        {
            var coords = new FlightState
            {
                X = int.MaxValue,
                Y = 0,
                Token = Guid.NewGuid().ToString("N")
            };

            var bf = new BinaryFormatter();
            using (var f = new FileStream("D:/temp/stream.bin", FileMode.Create))
            {
                bf.Serialize(f, coords);
            }

            // ReSharper disable once NotAccessedVariable
            FlightState c;
            using (var f = new FileStream("D:/temp/stream.bin", FileMode.Open))
            {
                // ReSharper disable once RedundantAssignment
                c = (FlightState) bf.Deserialize(f);
            }

            var server = new CarpetTracker("0.0.0.0", 12345);
            server.StartListener();
        }
    }
}
