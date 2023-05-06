// Write a webserver that queries the github API and returns the number of
// stars for a given repository in the response body.
package main

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"net/http"
)

type Repo struct {
	Name            string `json:"name"`
	StargazersCount int    `json:"stargazers_count"`
}

func main() {
	// implement the handler function that returns the number of stars for a given repository
	// in json response body
	http.HandleFunc("/stars", func(w http.ResponseWriter, r *http.Request) {
		// get the repo name from the query string
		repoParam := r.URL.Query().Get("repo")
		if repoParam == "" {
			http.Error(w, "repo query param is required", http.StatusBadRequest)
			return
		}

		// query the github API
		resp, err := http.Get(fmt.Sprintf("https://api.github.com/repos/%s", repoParam))
		if err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}
		defer resp.Body.Close()

		// read the response body
		body, err := ioutil.ReadAll(resp.Body)
		if err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}

		// unmarshal the response body into a Repo struct
		var repo Repo
		err = json.Unmarshal(body, &repo)
		if err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}

		// marshal the Repo struct into json
		body, err = json.Marshal(repo)
		if err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}

		// write the json response body
		w.Header().Set("Content-Type", "application/json")
		w.Write(body)
	})

	// start the server
	log.Fatal(http.ListenAndServe(":8080", nil))
}
