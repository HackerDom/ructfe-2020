package server

import (
	"context"
	"fmt"
	"github.com/HackerDom/ructfe2020/internal/manager"
	httprpc "github.com/HackerDom/ructfe2020/pkg/httprtc"
	pb "github.com/HackerDom/ructfe2020/proto"
	"github.com/go-chi/chi"
	"github.com/golang/protobuf/proto"
)

func NewDocuments(m *manager.Manager) *documentsService {
	return &documentsService{m: m}
}

type documentsService struct {
	m *manager.Manager
}

func (s *documentsService) Mount(mux *chi.Mux) {
	httprpc.New("POST", "/docs/create").
		Mount(mux).
		WithJSONPbReader(&pb.CreateDocumentRequest{}).
		WithJSONPbWriter().
		WithHandler(func(ctx context.Context, req proto.Message) (proto.Message, error) {
			return s.Create(ctx, req.(*pb.CreateDocumentRequest))
		})
	httprpc.New("POST", "/docs/list").
		Mount(mux).
		WithJSONPbReader(&pb.ListDocumentsRequest{}).
		WithJSONPbWriter().
		WithHandler(func(ctx context.Context, req proto.Message) (proto.Message, error) {
			return s.List(ctx, req.(*pb.ListDocumentsRequest))
		})
	httprpc.New("POST", "/docs/execute").
		Mount(mux).
		WithJSONPbReader(&pb.ListDocumentsRequest{}).
		WithJSONPbWriter().
		WithHandler(func(ctx context.Context, req proto.Message) (proto.Message, error) {
			return s.List(ctx, req.(*pb.ListDocumentsRequest))
		})
}

func (s *documentsService) List(ctx context.Context, req *pb.ListDocumentsRequest) (*pb.ListDocumentsResponse, error) {
	return nil, fmt.Errorf("not implemented")
}

func (s *documentsService) Create(ctx context.Context, req *pb.CreateDocumentRequest) (*pb.CreateDocumentResponse, error) {
	err := s.m.Create(req.Doc)
	if err != nil {
		return nil, err
	}
	return &pb.CreateDocumentResponse{}, nil
}

func (s *documentsService) Execute(ctx context.Context, req *pb.ExecuteRequest) (*pb.ExecuteResponse, error) {
	executed, err := s.m.ExecForUser(req.DocId, req.Username)
	if err != nil {
		return nil, err
	}
	return &pb.ExecuteResponse{Executed: executed}, nil
}
