const path = require('path');
const FixStyleOnlyEntriesPlugin = require('webpack-fix-style-only-entries');

module.exports = {
    entry: './src/index.js',
    output: {
        filename: 'main.bf.bundle.js',
        path: path.resolve(__dirname, 'static', 'assets'),
    },
    resolve: {
        alias: {
            '@': path.resolve(__dirname, './src/'),
        },
        extensions: ['*', '.js'],
    },
    module: {
        rules: [
            {
                test: /\.scss$/,
                exclude: /node_modules/,
                type: 'asset/resource',
                generator: {
                    filename: '[name].bf.build.css',
                },
                use: [
                    {
                        loader: 'sass-loader',
                    },
                ],
            },
        ],
    },
    plugins: [new FixStyleOnlyEntriesPlugin({ extensions: ['scss'] })],
};