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
            var coords = new Coords
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
            Coords c;
            using (var f = new FileStream("D:/temp/stream.bin", FileMode.Open))
            {
                // ReSharper disable once RedundantAssignment
                c = (Coords) bf.Deserialize(f);
            }

            var server = new CarpetTrackServer("0.0.0.0", 12345);
            server.StartListener();
        }
    }
}
