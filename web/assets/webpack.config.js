var path = require('path');

const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const FixStyleOnlyEntriesPlugin = require('webpack-fix-style-only-entries');
const ManifestPlugin = require('webpack-manifest-plugin');

module.exports = {
    mode: 'development',
    entry: {
        main:    './scripts/main.js',
        styles:  './styles/style.scss'
    },
    output: {
        //path: '../static',
        path: path.resolve(__dirname, "..", "static"),
        //publicPath: 'http://localhost:2992/assets/',
        //publicPath: 'http://localhost:5000/static/',
        filename: '[name].[chunkhash].js',
        //filename: '[name].js',
        //chunkFilename: '[id].[chunkhash].js'
    },
    devServer: {
        compress: false,
        watchContentBase: true,
        port: 9000,
        proxy: {
            '!(/static/**/**.*)': {
                target: 'http://127.0.0.1:5000',
            },
        },
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
                test: /\.css$/,
                use: [
                    {
                        loader: MiniCssExtractPlugin.loader,
                            /*options: {
                                // you can specify a publicPath here
                                // by default it uses publicPath in webpackOptions.output
                                publicPath: '../',
                                hmr: process.env.NODE_ENV === 'development',
                            },*/
                    },
                    'css-loader',
                ],
            },
            {
                test: /\.scss$/,
                use: [
                    {
                        loader: MiniCssExtractPlugin.loader,
                            /*options: {
                                // you can specify a publicPath here
                                // by default it uses publicPath in webpackOptions.output
                                publicPath: '../',
                                hmr: process.env.NODE_ENV === 'development',
                            },*/
                    },
                    {
                        loader: "css-loader" // translates CSS into CommonJS
                    },
                    {
                        loader: "sass-loader" // compiles Sass to CSS
                    }
                ]
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
        new FixStyleOnlyEntriesPlugin(),
        new MiniCssExtractPlugin({
            // Options similar to the same options in webpackOptions.output
            // both options are optional
            //filename: '[name].css',
            filename: '[name].[chunkhash].css',
            //filename: "style.[contenthash].css",
        }),
        new ManifestPlugin({
            fileName: 'manifest.json',
            stripSrc: true
        })
    ]
};
