namespace CarpetRadar.TrackServer
{
    class Program
    {
        static void Main()
        {
            var server = new CarpetTracker("0.0.0.0", 12345);
            server.StartListener();
        }
    }
}
