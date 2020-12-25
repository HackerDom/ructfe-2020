using System;

namespace CarpetRadar.Services.Models
{
    [Serializable]
    public class CurrentPosition
    {
        public int X { get; set; }
        public int Y { get; set; }

        public Guid UserId { get; set; }
        public Guid FlightId { get; set; }

        public string Label { get; set; }
        public bool Finished { get; set; }

        public DateTime ReportMoment { get; set; }
    }
}
