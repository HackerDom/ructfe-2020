using System.Net.Sockets;
using System.Text;

namespace CarpetRadar.Services
{
    public static class NetworkStreamExtensions
    {
        public static void Send(this NetworkStream stream, string message)
        {
            var bytes = Encoding.ASCII.GetBytes(message);
            stream.Write(bytes, 0, bytes.Length);
        }

        public static void TrySend(this NetworkStream stream, string message)
        {
            try
            {
                Send(stream, message);
            }
            catch
            {
            }
        }
    }
}
