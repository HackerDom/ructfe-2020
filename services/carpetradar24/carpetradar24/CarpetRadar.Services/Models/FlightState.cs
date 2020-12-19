using System;

namespace CarpetRadar.Services.Models
{
    [Serializable]
    public class FlightState
    {
        public string Token { get; set; }

        public int X { get; set; }
        public int Y { get; set; }

        public Guid FlightId { get; set; }

        public string Label { get; set; }
        public string License { get; set; }

        public bool Finished { get; set; }

    }
}
