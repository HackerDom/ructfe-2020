package docs

import (
	"fmt"
	pb "github.com/HackerDom/ructfe2020/proto"
)

var DocumentNotFoundErr = fmt.Errorf("document not found")

func NewInMemory() *InMemory {
	return &InMemory{docs: make([]*pb.Document, 0)}
}

type InMemory struct {
	docs []*pb.Document
}

func (s *InMemory) List() ([]*pb.Document, error) {
	return s.docs, nil
}

func (s *InMemory) Insert(document *pb.Document) error {
	s.docs = append(s.docs, document)
	return nil
}

func (s *InMemory) Delete(docID string) error {
	n := make([]*pb.Document, 0, len(s.docs))
	for _, doc := range s.docs {
		if doc.Id == docID {
			return nil
		}
		n = append(n, doc)
	}
	s.docs = n
	return nil
}

func (s *InMemory) Get(docID string) (*pb.Document, error) {
	for _, doc := range s.docs {
		if doc.Id == docID {
			return doc, nil
		}
	}
	return nil, DocumentNotFoundErr
}
