from code_generation.formatting import *

class Options:
    class Category:
        class Option:
            def __init__(self, id, name, inputHtml, storageSet, storageGet, elementSet, elementGet, configure, hint):
                self.id = id
                self.name = name
                self.inputHtml = inputHtml
                self.storageSet = storageSet
                self.storageGet = storageGet
                self.elementSet = elementSet
                self.elementGet = elementGet
                self.configure = configure
                self.hint = hint
            
            def get_html(self, odd):
                return f"""
                    <div class="row" {"odd" if odd else "even"}>
                        <span>{self.name} <div class="tooltip"><img class="info" src="images/info.svg" /><span class="tooltiptext">{self.hint}</span></div></span>
                        {self.inputHtml}
                    </div>"""
            
            def get_storage_set(self):
                return self.storageSet
            
            def get_storage_get(self):
                return self.storageGet
            
            def get_element_set(self):
                return self.elementSet
            
            def get_element_get(self):
                return self.elementGet
            
            def get_configure(self):
                return self.configure
        
        def __init__(self, name):
            self.options = []
            self.name = name
        
        def add_option(self, id, name, inputHtml, storageSet, storageGet, elementSet, elementGet, configure, hint):
            self.options.append(Options.Category.Option(id, name, inputHtml, storageSet, storageGet, elementSet, elementGet, configure, hint))
        
        def add_string_option(self, id, name, hint, defaultValue):
            inputHtml = f'<input type="text" id="{id}" />'
            storageSet = f'{id}: {id}'
            storageGet = f'{id}: "{defaultValue}"'
            elementSet = f'document.getElementById(\'{id}\').value = items.{id};'
            elementGet = f'const {id} = document.getElementById(\'{id}\').value;'
            configure = f'''
                if (this.configuration.{id} === undefined) {{
                    this.configuration.{id} = "{defaultValue}";
                }}
                '''
            self.add_option(id, name, inputHtml, storageSet, storageGet, elementSet, elementGet, configure, hint)
        
        def add_bool_option(self, id, name, hint, defaultValue):
            defaultString = "true" if defaultValue else "false"
            inputHtml = f'<input type="checkbox" id="{id}" value="true" />'
            storageSet = f'{id}: String({id})'
            storageGet = f'{id}: "{defaultString}"'
            elementSet = f'document.getElementById(\'{id}\').checked = (items.{id} === "true");'
            elementGet = f'const {id} = document.getElementById(\'{id}\').checked;'
            configure = f'''
                if (this.configuration.{id} === undefined) {{
                    this.configuration.{id} = {defaultString};
                }} else {{
                    this.configuration.{id} = (this.configuration.{id} === true) || (this.configuration.{id} === "true");
                }}
                '''
            self.add_option(id, name, inputHtml, storageSet, storageGet, elementSet, elementGet, configure, hint)
        
        def add_integer_option(self, id, name, hint, defaultValue, minValue = None, maxValue = None):
            minString = f'min="{minValue}"' if (minValue != None) else ""
            maxString = f'max="{maxValue}"' if (maxValue != None) else ""
            inputHtml = f'<input type="number" id="{id}" {minString} {maxString} />'
            storageSet = f'{id}: {id}'
            storageGet = f'{id}: "{defaultValue}"'
            elementSet = f'document.getElementById(\'{id}\').value = items.{id};'
            elementGet = f'const {id} = document.getElementById(\'{id}\').value;'
            configure = f'''
                if (this.configuration.{id} === undefined) {{
                    this.configuration.{id} = {defaultValue};
                }} else {{
                    this.configuration.{id} = Number(this.configuration.{id});
                }}
                '''
            self.add_option(id, name, inputHtml, storageSet, storageGet, elementSet, elementGet, configure, hint)
        
        def get_html(self):
            html = ""
            odd = True
            for option in self.options:
                html += option.get_html(odd)
                odd = not odd
            
            return f"""
            <div class="category" vbox>
                <h2>{self.name}</h2>
                
                <div class="options">{html}
                </div>
            </div>
            """
            
            return html
        
        def get_storage_set(self):
            js = ""
            for option in self.options:
                js += option.get_storage_set() + ',\n'
            return js
        
        def get_storage_get(self):
            js = ""
            for option in self.options:
                js += option.get_storage_get() + ',\n'
            return js
        
        def get_element_set(self):
            js = ""
            for option in self.options:
                js += option.get_element_set() + '\n'
            return js
        
        def get_element_get(self):
            js = ""
            for option in self.options:
                js += option.get_element_get() + '\n'
            return js
        
        def get_configure(self):
            js = ""
            for option in self.options:
                js += option.get_configure() + '\n'
            return js
    
    def __init__(self):
        self.categories = []
    
    def add_category(self, name):
        category = Options.Category(name)
        self.categories.append(category)
        return category
    
    def get_html(self):
        html = ""
        for category in self.categories:
            html += category.get_html()
        return html
    
    def get_save_options(self):
        js = """
            $ELEMENT_GET
            
            chrome.storage.local.set(
                {
                    $STORAGE_SET
                },
                () => {
                    // Update status to let user know options were saved.
                    const status = document.getElementById('status');
                    status.textContent = 'Options saved.';
                    setTimeout(() => {
                        status.textContent = '';
                    }, 750);
                }
            );
            """
        
        element_get = ""
        for category in self.categories:
            element_get += category.get_element_get()
        
        storage_set = ""
        for category in self.categories:
            storage_set += category.get_storage_set()

        return format(js.replace("$ELEMENT_GET", element_get).replace("$STORAGE_SET", storage_set), 1)

    def get_restore_options(self):
        js = """
            chrome.storage.local.get(
                {
                    $STORAGE_GET
                },
                (items) => {
                    $ELEMENT_SET
                }
            );"""
        
        storage_get = ""
        for category in self.categories:
            storage_get += category.get_storage_get()
        
        element_set = ""
        for category in self.categories:
            element_set += category.get_element_set()
        
        return format(js.replace("$STORAGE_GET", storage_get).replace("$ELEMENT_SET", element_set), 1)

    def get_load_options(self):
        js = """
            chrome.storage.local.get(
                {
                    $STORAGE_GET
                },
                (items) => {
                    window.dispatchEvent(new CustomEvent("__WebGPUReconstruct_options", { detail: JSON.stringify(items) }));
                }
            );"""
        
        storage_get = ""
        for category in self.categories:
            storage_get += category.get_storage_get()
        
        return format(js.replace("$STORAGE_GET", storage_get), 0)

    def get_configure(self):
        js = ""
        for category in self.categories:
            js += category.get_configure()
        return format(js, 2)

def get_options():
    options = Options()
    
    capture = options.add_category("Capture")
    capture.add_string_option("captureFilename", "Filename", "What to name the capture file.", "capture.wgpur")
    capture.add_integer_option("captureMaxFrames", "Max frames", "Automatically end the capture after n frames. 0 for no limit (capture has to be ended manually).", 0, 0, None)
    
    adapter = options.add_category("Adapter")
    adapter.add_bool_option("adapterDefaultLimits", "Force default limits", "Pretend the adapter only supports the default limits. Useful for testing and making captures more portable.", False)
    
    externalTextures = options.add_category("External textures")
    externalTextures.add_integer_option("externalTextureScale", "Scale (%)", "Downscale external textures to reduce capture file size.", 100, 1, 100)
    
    return options
