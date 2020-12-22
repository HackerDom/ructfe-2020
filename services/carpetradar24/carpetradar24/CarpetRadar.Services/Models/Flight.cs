using System;
using System.Collections.Generic;

namespace CarpetRadar.Services.Models
{
    public class Flight
    {
        public List<int> X { get; set; }
        public List<int> Y { get; set; }
        public List<DateTime> ReportMoments { get; set; }

        public Guid FlightId { get; set; }
        public string Label { get; set; }
        public string License { get; set; }

        public bool Finished { get; set; }
    }
}
