package server

import (
	"context"
	"github.com/HackerDom/ructfe2020/internal/manager"
	httprpc "github.com/HackerDom/ructfe2020/pkg/httprtc"
	pb "github.com/HackerDom/ructfe2020/proto"
	"github.com/go-chi/chi"
	"github.com/golang/protobuf/proto"
	"net/http"
)

func NewUsers(m *manager.Manager) *usersService {
	return &usersService{m: m}
}

type usersService struct {
	m *manager.Manager
}

// users service routes
const (
	loginPath    = "/users/login"
	registerPath = "/users/register"
	listPath     = "/users/list"
)

func (s *usersService) Mount(mux *chi.Mux) {
	httprpc.New("POST", registerPath).
		Mount(mux).
		WithJSONPbReader(&pb.RegisterRequest{}).
		WithJSONPbWriter().
		WithHandler(func(ctx context.Context, req proto.Message) (proto.Message, error) { return s.Register(ctx, req.(*pb.RegisterRequest)) })
	httprpc.New("POST", listPath).
		Mount(mux).
		WithJSONPbReader(&pb.ListRequest{}).
		WithJSONPbWriter().
		WithHandler(func(ctx context.Context, req proto.Message) (proto.Message, error) { return s.List(ctx, req.(*pb.ListRequest)) })
	httprpc.New("POST", loginPath).
		Mount(mux).
		WithJSONPbReader(&pb.LoginRequest{}).
		WithCustomWriter(func(w http.ResponseWriter, respPb proto.Message) error {
			resp := respPb.(*pb.LoginResponse)
			http.SetCookie(w, &http.Cookie{
				Name:  "session",
				Value: resp.Session,
			})
			return nil
		}).
		WithHandler(func(ctx context.Context, req proto.Message) (proto.Message, error) { return s.Login(ctx, req.(*pb.LoginRequest)) })
}

func (s *usersService) List(ctx context.Context, req *pb.ListRequest) (*pb.ListResponse, error) {
	// TODO: [12/13/20] (vaspahomov): pagination
	names, err := s.m.GetNames()
	if err != nil {
		return nil, err
	}
	return &pb.ListResponse{Usernames: names}, nil
}

func (s *usersService) Register(ctx context.Context, req *pb.RegisterRequest) (*pb.RegisterResponse, error) {
	u, err := s.m.RegisterUser(req.Name, req.Password, req.Bio)
	if err != nil {
		return nil, err
	}
	return &pb.RegisterResponse{
		User: u,
	}, nil
}

func (s *usersService) Login(ctx context.Context, req *pb.LoginRequest) (*pb.LoginResponse, error) {
	// TODO: [12/21/20] (vaspahomov):
	panic("not implemented")
	return &pb.LoginResponse{}, nil
}