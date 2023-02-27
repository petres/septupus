var path = require('path');

const { WebpackManifestPlugin } = require('webpack-manifest-plugin');
// const HtmlWebpackPlugin = require('html-webpack-plugin')

module.exports = {
    mode: 'development',
    entry: {
        main:    './src/main.js',
    },
    output: {
        //path: '../static',
        path: path.resolve(__dirname, "..", "static"),
        //publicPath: 'http://localhost:2992/assets/',
        //publicPath: 'http://localhost:5000/static/',
        publicPath: '',
        filename: '[name].[chunkhash].js',
        //filename: '[name].js',
        //chunkFilename: '[id].[chunkhash].js'
    },
    devServer: {
        compress: false,
        // watchContentBase: true,
        // port: 9000,
        // proxy: {
        //     '!(/static/**/**.*)': {
        //         target: 'http://127.0.0.1:5000',
        //     },
        // },
    },
    module: {
        rules: [
            {
                test: /\.js$/,
                exclude: /node_modules/,
                use: {
                    loader: "babel-loader"
                }
            },
            {
                test: /\.css$/i,
                use: ["style-loader", "css-loader"],
            },
            {
                test: /\.scss$/i,
                use: ["style-loader", "css-loader", "sass-loader"],
            },
            {
                test: /\.(woff(2)?|ttf|eot|svg)(\?v=\d+\.\d+\.\d+)?$/,
                use: [
                    {
                        loader: 'file-loader',
                        options: {
                            name: '[name].[ext]',
                            outputPath: 'fonts/'
                        }
                    }
                ]
            },
            {
                test: /\.ico$/,
                use: [
                    {
                        loader: 'file-loader',
                        options: {
                            name: '[name].[ext]',
                            outputPath: 'icons/'
                        }
                    }
                ]
            }
        ],
    },
    plugins: [
        // new HtmlWebpackPlugin(),
        new WebpackManifestPlugin({
            fileName: 'manifest.json',
            basePath: ''
        })
    ]
};
