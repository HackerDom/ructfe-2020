package randomSploit

import (
	//"fmt"
	"net/http"
	//"math/rand"
	"encoding/json"
	"io/ioutil"
)

const (
	url = "http://localhost:8080"
	usrs = "/users/list"

)

type User struct {
	name string
}

func main()  {
	resp, err := http.Post(url + usrs, "application/json", nil)
	if err != nil {
		panic(err)
	}
	defer resp.Body.Close()
	body, _ := ioutil.ReadAll(resp.Body)
	usernames := map[string]User{}
	err = json.Unmarshal(body, &usernames)
}
