from typing import Dict, Tuple
import jwt

secret = "G+KbPeShVmYq3t6w9z$C&F)J@McQfTjW"

exAdminToken = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI4NDcwMTVjOC1kODI4LTQwNGUtYjg3OC1lYThlNTRhMzk5ZDkiLCJpc3MiOiJ1c2VyLXNlcnZpY2UiLCJhdWQiOiJtcGNzNTEyMDUiLCJlbWFpbCI6Im1hdHRAbXBjcy5jb20iLCJuYW1lIjoibWF0dCIsImF1dGhvcml0aWVzIjpbIlJPTEVfVVNFUiIsIlJPTEVfQURNSU4iXSwiaWF0IjoxNjY5NDA4MDY2LCJleHAiOjE2NzIwMDAwNjZ9.N1x3fIBUz9CLDtabc9Lig6a4VFmRPdQaJwYX2Vabov0"
exUserToken = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJlN2YxNDI0OC03MWM3LTQ5MGQtOWYzOC0yNDdiMjRmNzI4YWEiLCJpc3MiOiJ1c2VyLXNlcnZpY2UiLCJhdWQiOiJtcGNzNTEyMDUiLCJlbWFpbCI6Im1hdHRfQG1wY3MuY29tIiwibmFtZSI6Im1hdHQiLCJhdXRob3JpdGllcyI6WyJST0xFX1VTRVIiXSwiaWF0IjoxNjY5NDA4MDk1LCJleHAiOjE2NzIwMDAwOTV9.j0_T0boKVL0MMpTmI_xSUfc3M25MoWqeo-Sdg9fVelQ"
mattToken = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJjMDM4MmQyYy1iYTVlLTQxZDgtYTYzYi00YjMzNDlkN2Q4YTMiLCJhdWQiOiJtcGNzNTEyMDUiLCJpc3MiOiJ1c2VyLXNlcnZpY2UiLCJuYW1lIjoibWF0dCIsImV4cCI6MTY3MDA1Nzc4NSwiaWF0IjoxNjcwMDE0NTg1LCJlbWFpbCI6Im1hdHRAbXBjcy5jb20iLCJhdXRob3JpdGllcyI6WyJST0xFX1VTRVIiLCJST0xFX0FETUlOIl19.tPsUVZex3evg-ZE7e2vUbRt7XHYhABMoodsqy0FYohA"
illToken = "asdfasdf"
aBidder = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiI4MmRhMzUxOC0xMDQ0LTRlOWItODQ1Yy1kZGMyYmI4MmViNGQiLCJhdWQiOiJtcGNzNTEyMDUiLCJpc3MiOiJ1c2VyLXNlcnZpY2UiLCJuYW1lIjoiTGF5VXN5RTBPa1piQUtWIiwiZXhwIjoxNjcwMDYwMDYwLCJpYXQiOjE2NzAwMTY4NjAsImVtYWlsIjoiTGF5VXN5RTBPa1piQUtWQG1wY3MuY29tIiwiYXV0aG9yaXRpZXMiOlsiUk9MRV9VU0VSIl19.jyQf2_XJNWnLjCm8sQJ-H39eFIuX45U1FbC9JuFFTEw"

aud = "mpcs51205"

# const (
# 	Secret = "G+KbPeShVmYq3t6w9z$C&F)J@McQfTjW"
# )

# type JwtParser struct {
# 	secret        string
# 	secretAsBytes []byte
# }

# func NewJwtParser(secret string) *JwtParser {
# 	return &JwtParser{
# 		secret:        secret,
# 		secretAsBytes: []byte(secret),
# 	}
# }

class JwtParser():

    def __init__(self, secret: str) -> None:
        self._secret = secret
        pass

    def parse(self,token: str) -> Dict[str,str]:
        return jwt.decode(token,key=self._secret, audience=aud,algorithms=["HS256"] ) 

class Authenticator():

    def __init__(self, jwtParser : JwtParser) -> None:
        self._jwtParser = jwtParser

    def extract_user_id(self,token:str) -> Tuple[str,bool]:
        """extracts user id from jwt; returns (user_id, false) on success,
        ("",true) on failure. the bool represents 'withErrors'."""
        try:
            data = self._jwtParser.parse(token)
        except:
            return "", True
        user_id = data["sub"]
        return user_id, False

    def is_admin(self,token:str) -> bool:
        try:
            data = self._jwtParser.parse(token)
        except:
            return False
        return "ROLE_ADMIN" in data["authorities"]

    def is_user(self,token:str) -> bool:
        try:
            data = self._jwtParser.parse(token)
        except:
            return False
        return "ROLE_USER" in data["authorities"]

if __name__ == "__main__":
    auth = Authenticator(JwtParser(secret=secret))
    userid, withErrs = auth.extract_user_id(exAdminToken)
    print(userid, withErrs)
    userid, withErrs = auth.extract_user_id(exUserToken)
    print(userid, withErrs)
    userid, withErrs = auth.extract_user_id(illToken)
    print(userid, withErrs)
    userid, withErrs = auth.extract_user_id(aBidder)
    print(userid, withErrs)

    userid = auth.is_admin(aBidder)
    print(userid)
    userid = auth.is_user(aBidder)
    print(userid)
    userid = auth.is_admin(exAdminToken)
    print(userid)

# 	jwtParser = NewJwtParser(secret)
# 	authenticator = NewAuthenticator(jwtParser)
# 	res1 = authenticator.IsAdmin(exAdminToken) // expect true
# 	res2 = authenticator.IsUser(exUserToken)   // expect true
# 	res3 = authenticator.IsAdmin(exUserToken)  // expect false
# 	res4 = authenticator.IsUser(exUserToken)   // expect true
# 	res5 = authenticator.IsAdmin(illToken)     // expect false
# 	res6 = authenticator.IsUser(illToken)      // expect false
# 	res7 = authenticator.IsAdmin(illToken)     // expect false
# 	res8 = authenticator.IsUser(illToken)      // expect false

# 	fmt.Println(res5)
# 	fmt.Println(res6)
# 	fmt.Println(res7)
# 	fmt.Println(res8)

# 	fmt.Println(authenticator.IsAdmin(aBidder))
# 	fmt.Println(authenticator.IsUser(aBidder))


# package security

# import (
# 	"fmt"
# 	"log"

# 	"github.com/golang-jwt/jwt/v4"
# )


# func (jwtParser *JwtParser) Parse(tokenString string) (map[string]interface{}, error) {
# 	log.Printf("[JwtParser] authenticating bearer token %s\n", tokenString)
# 	// alertEngine.sendToConsole(msg)
# 	// see: https://pkg.go.dev/github.com/golang-jwt/jwt/v4#example-Parse-Hmac

# 	claims = jwt.MapClaims{}

# 	// Parse takes the token string and a function for looking up the key. The latter is especially
# 	// useful if you use multiple keys for your application.  The standard is to use 'kid' in the
# 	// head of the token to identify which key to use, but the parsed token (head and claims) is provided
# 	// to the callback, providing flexibility.
# 	token, err = jwt.ParseWithClaims(tokenString, claims, func(token *jwt.Token) (interface{}, error) {
# 		// Don't forget to validate the alg is what you expect:
# 		if _, ok = token.Method.(*jwt.SigningMethodHMAC); !ok {
# 			return nil, fmt.Errorf("Unexpected signing method: %v", token.Header["alg"])
# 		}

# 		// hmacSampleSecret is a []byte containing your secret, e.g. []byte("my_secret_key")
# 		return jwtParser.secretAsBytes, nil
# 	})
# 	if err != nil {
# 		return nil, err
# 	}

# 	payload = map[string]interface{}{}
# 	if claims, ok = token.Claims.(jwt.MapClaims); ok && token.Valid {
# 		for key, val = range claims {
# 			payload[key] = val
# 		}
# 		return payload, nil
# 	} else {
# 		log.Println("[JwtParser] could not validate token; provided token invalid, or information was parsed incorrectly from valid token")
# 		return payload, err
# 	}
# }

# type Authenticator struct {
# 	jwtParser *JwtParser
# }

# func NewAuthenticator(jwtParser *JwtParser) *Authenticator {
# 	return &Authenticator{
# 		jwtParser: jwtParser,
# 	}
# }

# func (authenticator *Authenticator) extractDetails(tokenString string) (map[string]interface{}, error) {
# 	payload, err = authenticator.jwtParser.Parse(tokenString)
# 	return payload, err
# }

# func (authenticator *Authenticator) IsAdmin(tokenString string) bool {
# 	payload, err = authenticator.extractDetails(tokenString)
# 	if err != nil {
# 		return false // trivial fail
# 	}
# 	for key, val = range payload {
# 		if key == "authorities" {
# 			roles = val.([]interface{})
# 			for _, role = range roles {
# 				if role.(string) == "ROLE_ADMIN" {
# 					return true
# 				}
# 			}
# 		}
# 	}
# 	return false
# }

# func (authenticator *Authenticator) IsUser(tokenString string) bool {
# 	payload, err = authenticator.extractDetails(tokenString)
# 	if err != nil {
# 		return false // trivial fail
# 	}
# 	for key, val = range payload {
# 		if key == "authorities" {
# 			roles = val.([]interface{})
# 			for _, role = range roles {
# 				if role.(string) == "ROLE_USER" {
# 					return true
# 				}
# 			}
# 		}
# 	}
# 	return false
# }

# func (authenticator *Authenticator) MeetsRequirements(tokenString string, mustBeUser, mustBeAdmin bool) bool {
# 	payload, err = authenticator.extractDetails(tokenString)
# 	if err != nil {
# 		return false // trivial fail
# 	}
# 	isAdmin = false
# 	isUser = false
# 	for key, val = range payload {
# 		if key == "authorities" {
# 			roles = val.([]interface{})
# 			for _, role = range roles {
# 				if role.(string) == "ROLE_ADMIN" {
# 					isAdmin = true
# 				}
# 				if role.(string) == "ROLE_USER" {
# 					isUser = true
# 				}
# 			}
# 		}
# 	}
# 	meetsRequirements = true
# 	if mustBeAdmin && !isAdmin {
# 		meetsRequirements = false
# 	}
# 	if mustBeUser && !isUser {
# 		meetsRequirements = false
# 	}
# 	return meetsRequirements
# }

# func (authenticator *Authenticator) ExtractUserId(tokenString string) (string, bool) {
# 	payload, err = authenticator.extractDetails(tokenString)
# 	if err != nil {
# 		return "", true // trivial fail
# 	}
# 	for key, val = range payload {
# 		if key == "sub" {
# 			userId = val.(string)
# 			return userId, false
# 		}
# 	}
# 	return "", true
# }
