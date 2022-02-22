# Sublime Text 3 Local Pod Package


### A [Cocoapods](https://cocoapods.org/) plugin for automatically replacing your pods with local pods

### How it works

Press `Cmd + Shift + P` for Mac and `Ctrl + Shift + P` for Linux/Windows.

Input `Localpod` and select `Localpod: Find and Replace`, select desired pods and press `Done` to finish.

To make it work and work fast, several settings are necessary.

```
{
    "work_directory": "~/Documents/iOS",

    "abs_paths_for_pods": {
        "AFNetworking": "~/Documents/iOS/AFNetworking",
        

        "MyAwesomeToast": "~/Documents/iOS/MyApp/Libs/MyAwesomeToast",
        "AnotherExamplePod": "~/Documents/iOS/MyApp/Libs/AnotherExamplePod",
    },
}
```

`work_directory` is used for searching for the local pod path. You certainly don't want this package to walk through your whole computer :]

`abs_paths_for_pods` is not necessary. Anytime you specify a new pod, this package will search in `work_directory` and save the result in this map automatically once found. But if searching is too slow for you, you can manually edit this map.

### Installation

#### Package Control (TBD)

#### Manual Installation

On Mac:

```
git clone https://github.com/ijoyc/Localpod ~/Library/Application\ Support/Sublime\ Text\ 3/Packages/Localpod
```
