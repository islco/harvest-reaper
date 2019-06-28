const path = require("path");

module.exports = {
  entry: "./harvestreaper/static_raw/js/index.js",
  output: {
    filename: "main.js",
    path: path.resolve(__dirname, "harvestreaper/static/js")
  }
};
