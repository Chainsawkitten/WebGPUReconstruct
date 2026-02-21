#include "TestApp.hpp"

#include <game-activity/GameActivity.cpp>
#include <game-text-input/gametextinput.cpp>
#include <string>
#include <vector>
#include "Configuration.hpp"
#include "Logging.hpp"

std::vector<std::string> GetCommandLineArguments(struct android_app* app) {
    JNIEnv* environment;
    std::vector<std::string> arguments;
    
    if (app->activity->vm->AttachCurrentThread(&environment, NULL) != JNI_OK) {
        WebGPUNativeReplay::Logging::Error("Failed to attach current thread to VM.");
        return arguments;
    }
    
    jobject me = app->activity->javaGameActivity;

    jclass activityClass = environment->GetObjectClass(me);
    jmethodID getIntentMethod = environment->GetMethodID(activityClass, "getIntent", "()Landroid/content/Intent;");
    jobject intent = environment->CallObjectMethod(me, getIntentMethod);

    if (intent != nullptr) {
        jclass intentClass = environment->GetObjectClass(intent);
        jmethodID getStringExtraMethod = environment->GetMethodID(intentClass, "getStringExtra", "(Ljava/lang/String;)Ljava/lang/String;");

        jstring argsParam = environment->NewStringUTF("args");
        jstring jsParam = static_cast<jstring>(environment->CallObjectMethod(intent, getStringExtraMethod, argsParam));

        if (jsParam != nullptr) {
            const char *param = environment->GetStringUTFChars(jsParam, 0);
            if (param != nullptr) {
                // Split argument list.
                std::string stringParam = param;
                size_t start = 0;
                bool empty = true;
                for (size_t i = 0; i < stringParam.size(); ++i) {
                    if (stringParam[i] == ' ') {
                        if (!empty) {
                            arguments.push_back(stringParam.substr(start, i - start));
                        }
                        start = i + 1;
                        empty = true;
                    } else {
                        empty = false;
                    }
                }
                if (!empty) {
                    arguments.push_back(stringParam.substr(start));
                }
                
                environment->ReleaseStringUTFChars(jsParam, param);
            }
            environment->DeleteLocalRef(jsParam);
        }
        
        environment->DeleteLocalRef(argsParam);
        environment->DeleteLocalRef(intent);
    }

    app->activity->vm->DetachCurrentThread();
    
    return arguments;
}

WebGPUNativeReplay::Window window;
WebGPUNativeReplay::Configuration* configuration = nullptr;
bool started = false;
bool terminated = false;

extern "C" {

#include <game-activity/native_app_glue/android_native_app_glue.c>

void HandleCmd(android_app* app, int32_t cmd) {
    switch (cmd) {
        case APP_CMD_INIT_WINDOW:
        {
            if (!terminated) {
                window.window = app->window;

                configuration->width = ANativeWindow_getWidth(window.window);
                configuration->height = ANativeWindow_getHeight(window.window);
                WebGPUNativeReplay::Logging::Info("Filename: " + configuration->filename);

                started = true;
            }
            break;
        }
        case APP_CMD_TERM_WINDOW:
            terminated = true;
            break;
        default:
            break;
    }
}

void android_main(struct android_app* app) {
    started = false;
    terminated = false;

    // Handle intext extras (command line arguments).
    std::vector<std::string> arguments = GetCommandLineArguments(app);
    configuration = new WebGPUNativeReplay::Configuration(arguments);

    if (configuration->showVersion) {
        WebGPUNativeReplay::Configuration::ShowVersion();
        GameActivity_finish(app->activity);
        terminated = true;
    } else if (configuration->filename.empty() || configuration->showHelp) {
        WebGPUNativeReplay::Configuration::ShowHelp();
        GameActivity_finish(app->activity);
        terminated = true;
    }

    // Register an event handler for Android events
    app->onAppCmd = HandleCmd;

    // This sets up a typical game/event loop. It will run until the app is destroyed.
    int events;
    android_poll_source *pSource;
    do {
        // Process all pending events before running game logic.
        while (ALooper_pollOnce(0, nullptr, &events, (void **) &pSource) >= 0) {
            if (pSource) {
                pSource->process(app, pSource);
            }
        }
        
        if (started) {
            WebGPUNativeReplay::TestApp testApp(window, *configuration);
            testApp.RunCapture(configuration->filename, [&events, pSource, app]() {
                while (ALooper_pollOnce(0, nullptr, &events, (void **) &pSource) >= 0) {
                    if (pSource) {
                        pSource->process(app, pSource);
                    }
                }
                return !terminated;
            });
            GameActivity_finish(app->activity);
            started = false;
        }
    } while (!app->destroyRequested);
    
    delete configuration;
}
}
