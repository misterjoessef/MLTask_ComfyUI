import { app } from "../../scripts/app.js";
import { $el } from "../../scripts/ui.js";
import { api } from "../../scripts/api.js";
import { ComfyWidgets } from "../../scripts/widgets.js";

function show_message(msg) {
  app.ui.dialog.show(msg);
  app.ui.dialog.element.style.zIndex = 10010;
}

async function getTokenFromServer() {
  const response = await api.fetchApi("/socialman/token", {
    method: "GET",
  });
  const data = await response.json();
  return data.token;
}
async function setTokenInServer(node_id, token) {
  const body = new FormData();
  body.append("token", token);
  body.append("node_id", node_id);
  const response = await api.fetchApi("/socialman/token", {
    method: "POST",
    body,
  });
  return response;
}
async function setPasswordInServer(node_id, token) {
  const body = new FormData();
  body.append("password", token);
  body.append("node_id", node_id);
  const response = await api.fetchApi("/socialman/password", {
    method: "POST",
    body,
  });
  return response;
}
// Adds an upload button to the nodes
//custom nodes reference
// web/extensions/core/noteNode.js
const convertIdClass = (text) => text.replaceAll(".", "_");
const idExt = "mltask.socialman";

function renderHeader(name) {
  return $el("td", [
    $el("label", {
      textContent: name,
      for: convertIdClass(`${idExt}.mltask.socialman.token`),
    }),
  ]);
}
var socialManToken = "****";

function renderGetTokenButton() {
  return $el("button", {
    textContent: "Show token",
    onclick: () => {},
    style: {
      display: "block",
      width: "100%",
    },
  });
}

function renderTokenlabel(val) {
  return $el("label", {
    style: { display: "flex" },
    textContent: `Social Man Token:`,
    for: convertIdClass(`${idExt}.mltask.socialman.token`),
  });
}
function renderTokenToken(val) {
  return $el("label", {
    style: { display: "flex", fontWeight: "bold" },
    textContent: `${socialManToken}`,
    for: convertIdClass(`${idExt}.mltask.socialman.token`),
  });
}
function renderSettings(name, val) {
  // return $el("td", [renderTokenTextField(val), renderGetTokenButton()]);
  return $el("td", [renderTokenlabel(val), renderTokenToken(val)]);
}
var statusMessage = "123";
var currentInputToken = "";
app.registerExtension({
  name: `${idExt}.poster`,
  async init() {
    socialManToken = await getTokenFromServer();
    app.ui.settings.addSetting({
      id: `${idExt}.mltask`,
      name: "🤖 MLTask",
      defaultValue: true,
      type: (name, sett, val) => {
        return $el("tr", [renderHeader(name), renderSettings(name, val)]);
      },
    });
  },
  getCustomWidgets(app) {
    return {
      STRING_URL: (node, inputName, inputData, app) => {
        const container = $el("div", {
          style: {
            height: "100%",
            margin: 0,
            padding: 0,
            display: "flex",
          },
        });
        const openPostButton = $el("button", {
          textContent: "Open Post on SocialMan",
          style: {
            backgroundColor: "#58c7f3",
            width: "100%",
          },
          onclick: async () => {
            window.open(inputData.value);
          },
        });
        container.appendChild(openPostButton);
        const linkWidget = node.addDOMWidget(
          inputName,
          "container",
          container,
          {
            getValue() {
              return node.widgets[0].value;
            },
            setValue(v) {
              inputData.value = node.widgets[0].value;
            },
          }
        );
        return { widget: linkWidget };
      },
      DISPLAY_MSG: (node, inputName, inputData, app) => {
        console.log("node = ");
        console.log(node);
        console.log("=====");
        const container = $el("div", {
          style: {
            height: "20px",
            margin: 0,
            padding: 0,
            display: "flex",
          },
        });
        const messageLabel = $el(
          "label",
          {
            style: {
              color: "#f8f8f8",
              display: "block",
              margin: "10px 0 0 0",
              fontWeight: "bold",
              textDecoration: "none",
            },
          },
          [statusMessage]
        );
        container.appendChild(messageLabel);
        const widget = node.addDOMWidget(inputName, "container", container);

        return {
          widget,
        };
      },
      SM_TOKEN: (node, inputName, inputData, app) => {
        const tokenSetDiv = $el("div", {
          style: {
            height: "20px",
            margin: 0,
            padding: 0,
            display: "flex",
          },
        });

        const tokenInput = $el("input", {
          type: "password",
          style: {
            width: "55%",
          },
          value:
            inputData[1]?.default ||
            "put your token here and DO NOT SHARE IT WITH ANYONE",
          oninput: () => {
            currentInputToken = tokenInput.value;
          },
        });
        tokenInput.addEventListener("focus", function () {
          // Your function when the input field is clicked (focused)
          tokenInput.value = "";
          // You can add any additional functionality here
        });

        tokenInput.addEventListener("blur", function () {
          tokenInput.value =
            "put your token here and DO NOT SHARE IT WITH ANYONE";
        });
        const setTokenButton = $el("button", {
          textContent: "Set Token",
          style: {
            backgroundColor: "#58c7f3",
            width: "45%",
          },
          onclick: async () => {
            try {
              const response = await setTokenInServer(
                node.id,
                currentInputToken
              );
              const data = await response.json();
              if (!response.ok) {
                throw new Error(
                  data.message || "An error occurred while setting the token"
                );
              }
              show_message("Token Set 🎉");
            } catch (error) {
              show_message(error.message);
            }

            currentInputToken = "";
          },
        });
        tokenSetDiv.appendChild(tokenInput);
        tokenSetDiv.appendChild(setTokenButton);

        const passwordSetDiv = $el("div", {
          style: {
            height: "20px",
            margin: 0,
            padding: 0,
            display: "flex",
          },
        });

        const passwordInput = $el("input", {
          type: "password",
          style: {
            width: "45%",
          },
          value:
            inputData[1]?.default ||
            "put your token here and DO NOT SHARE IT WITH ANYONE",
          oninput: () => {
            currentInputToken = passwordInput.value;
          },
        });
        passwordInput.addEventListener("focus", function () {
          // Your function when the input field is clicked (focused)
          passwordInput.value = "";
          // You can add any additional functionality here
        });

        passwordInput.addEventListener("blur", function () {
          passwordInput.value =
            "put your password here and DO NOT SHARE IT WITH ANYONE";
        });
        const setPasswordButton = $el("button", {
          textContent: "Set Password",
          style: {
            backgroundColor: "#58c7f3",
            width: "55%",
          },
          onclick: async () => {
            try {
              const response = await setPasswordInServer(
                node.id,
                currentInputToken
              );
              const data = await response.json();
              if (!response.ok) {
                throw new Error(
                  data.message || "An error occurred while setting the password"
                );
              }
              show_message("Password Set 🎉");
            } catch (error) {
              show_message(error.message);
            }

            currentInputToken = "";
          },
        });
        passwordSetDiv.appendChild(passwordInput);
        passwordSetDiv.appendChild(setPasswordButton);

        let getNewTokenDiv = $el("div", {
          style: {
            height: "20px",
            margin: 0,
            padding: 0,
            display: "flex",
          },
        });
        let getNewTokenButton = $el("button", {
          textContent: "Get New Token",
          style: {
            backgroundColor: "#ffd40d",
            width: "100%",
          },
          onclick: () => {
            window.open("https://mltask.com/user/comfyui");
          },
        });
        getNewTokenDiv.appendChild(getNewTokenButton);

        const container = $el("div", {
          style: {
            height: "100%",
            margin: 0,
            padding: 0,
            display: "flex",
          },
        });

        container.appendChild(tokenSetDiv);
        container.appendChild(passwordSetDiv);
        container.appendChild(getNewTokenDiv);

        const tokenWidget = node.addDOMWidget(
          inputName,
          "container",
          container,
          {
            getHeight() {
              return 80;
            },
            getValue() {
              return tokenInput.value;
            },
            setValue(v) {
              tokenInput.value = v;
            },
          }
        );
        tokenWidget.serialize = false;

        return {
          widget: tokenWidget,
        };
      },
      BETTER_IMAGE_UPLOAD(node, inputName, inputData, app) {
        const targetInputName = inputName.split("__")[0];
        const imageWidget = node.widgets.find(
          (w) => w.name === (inputData[1]?.widget ?? targetInputName)
        );
        let uploadWidget;

        function showImage(name) {
          const img = new Image();
          img.onload = () => {
            node.imgs = [img];
            app.graph.setDirtyCanvas(true);
          };
          let folder_separator = name.lastIndexOf("/");
          let subfolder = "";
          if (folder_separator > -1) {
            subfolder = name.substring(0, folder_separator);
            name = name.substring(folder_separator + 1);
          }
          img.src = api.apiURL(
            `/view?filename=${encodeURIComponent(
              name
            )}&type=input&subfolder=${subfolder}${app.getPreviewFormatParam()}${app.getRandParam()}`
          );
          node.setSizeForImage?.();
        }

        var default_value = imageWidget.value;
        Object.defineProperty(imageWidget, "value", {
          set: function (value) {
            this._real_value = value;
          },

          get: function () {
            let value = "";
            if (this._real_value) {
              value = this._real_value;
            } else {
              return default_value;
            }

            if (value.filename) {
              let real_value = value;
              value = "";
              if (real_value.subfolder) {
                value = real_value.subfolder + "/";
              }

              value += real_value.filename;

              if (real_value.type && real_value.type !== "input")
                value += ` [${real_value.type}]`;
            }
            return value;
          },
        });

        // Add our own callback to the combo widget to render an image when it changes
        const cb = node.callback;
        imageWidget.callback = function () {
          showImage(imageWidget.value);
          if (cb) {
            return cb.apply(this, arguments);
          }
        };

        // On load if we have a value then render the image
        // The value isnt set immediately so we need to wait a moment
        // No change callbacks seem to be fired on initial setting of the value
        requestAnimationFrame(() => {
          if (imageWidget.value) {
            showImage(imageWidget.value);
          }
        });

        async function uploadFile(file, updateNode, pasted = false) {
          try {
            // Wrap file in formdata so it includes filename
            const body = new FormData();
            body.append("image", file);
            if (pasted) body.append("subfolder", "pasted");
            const resp = await api.fetchApi("/upload/image", {
              method: "POST",
              body,
            });

            if (resp.status === 200) {
              const data = await resp.json();
              // Add the file to the dropdown list and update the widget value
              let path = data.name;
              if (data.subfolder) path = data.subfolder + "/" + path;

              if (!imageWidget.options.values.includes(path)) {
                imageWidget.options.values.push(path);
              }

              if (updateNode) {
                showImage(path);
                imageWidget.value = path;
              }
            } else {
              alert(resp.status + " - " + resp.statusText);
            }
          } catch (error) {
            alert(error);
          }
        }

        const fileInput = document.createElement("input");
        Object.assign(fileInput, {
          type: "file",
          accept: "image/jpeg,image/png,image/webp",
          style: "display: none",
          onchange: async () => {
            if (fileInput.files.length) {
              await uploadFile(fileInput.files[0], true);
            }
          },
        });
        document.body.append(fileInput);

        // Create the button widget for selecting the files
        uploadWidget = node.addWidget("button", inputName, "image", () => {
          fileInput.click();
        });
        uploadWidget.label = "choose file to upload";
        uploadWidget.serialize = false;

        // Add handler to check if an image is being dragged over our node
        node.onDragOver = function (e) {
          if (e.dataTransfer && e.dataTransfer.items) {
            const image = [...e.dataTransfer.items].find(
              (f) => f.kind === "file"
            );
            return !!image;
          }

          return false;
        };

        // On drop upload files
        node.onDragDrop = function (e) {
          console.log("onDragDrop called");
          let handled = false;
          for (const file of e.dataTransfer.files) {
            if (file.type.startsWith("image/")) {
              uploadFile(file, !handled); // Dont await these, any order is fine, only update on first one
              handled = true;
            }
          }

          return handled;
        };

        node.pasteFile = function (file) {
          if (file.type.startsWith("image/")) {
            const is_pasted =
              file.name === "image.png" &&
              file.lastModified - Date.now() < 2000;
            uploadFile(file, true, is_pasted);
            return true;
          }
          return false;
        };

        return { widget: uploadWidget };
      },
    };
  },
  registerCustomNodes() {
    // class BetterRerouteNode {
    //   color = LGraphCanvas.node_colors.yellow.color;
    //   // bgcolor = LGraphCanvas.node_colors.yellow.bgcolor;
    //   bgcolor = "#FFF000";
    //   groupcolor = LGraphCanvas.node_colors.yellow.groupcolor;
    //   constructor() {
    //     if (!this.properties) {
    //       this.properties = {};
    //     }
    //     this.properties.showOutputText = BetterRerouteNode.defaultVisibility;
    //     this.properties.horizontal = false;
    //     this.addInput("", "*");
    //     this.addOutput(this.properties.showOutputText ? "*" : "", "*");
    //     this.onAfterGraphConfigured = function () {
    //       requestAnimationFrame(() => {
    //         this.onConnectionsChange(LiteGraph.INPUT, null, true, null);
    //       });
    //     };
    //     this.onConnectionsChange = function (
    //       type,
    //       index,
    //       connected,
    //       link_info
    //     ) {
    //       this.applyOrientation();
    //       // Prevent multiple connections to different types when we have no input
    //       if (connected && type === LiteGraph.OUTPUT) {
    //         // Ignore wildcard nodes as these will be updated to real types
    //         const types = new Set(
    //           this.outputs[0].links
    //             .map((l) => app.graph.links[l].type)
    //             .filter((t) => t !== "*")
    //         );
    //         if (types.size > 1) {
    //           const linksToDisconnect = [];
    //           for (let i = 0; i < this.outputs[0].links.length - 1; i++) {
    //             const linkId = this.outputs[0].links[i];
    //             const link = app.graph.links[linkId];
    //             linksToDisconnect.push(link);
    //           }
    //           for (const link of linksToDisconnect) {
    //             const node = app.graph.getNodeById(link.target_id);
    //             node.disconnectInput(link.target_slot);
    //           }
    //         }
    //       }
    //       // Find root input
    //       let currentNode = this;
    //       let updateNodes = [];
    //       let inputType = null;
    //       let inputNode = null;
    //       while (currentNode) {
    //         updateNodes.unshift(currentNode);
    //         const linkId = currentNode.inputs[0].link;
    //         if (linkId !== null) {
    //           const link = app.graph.links[linkId];
    //           if (!link) return;
    //           const node = app.graph.getNodeById(link.origin_id);
    //           const type = node.constructor.type;
    //           if (type === "Better Reroute") {
    //             if (node === this) {
    //               // We've found a circle
    //               currentNode.disconnectInput(link.target_slot);
    //               currentNode = null;
    //             } else {
    //               // Move the previous node
    //               currentNode = node;
    //             }
    //           } else {
    //             // We've found the end
    //             inputNode = currentNode;
    //             inputType = node.outputs[link.origin_slot]?.type ?? null;
    //             break;
    //           }
    //         } else {
    //           // This path has no input node
    //           currentNode = null;
    //           break;
    //         }
    //       }
    //       // Find all outputs
    //       const nodes = [this];
    //       let outputType = null;
    //       while (nodes.length) {
    //         currentNode = nodes.pop();
    //         const outputs =
    //           (currentNode.outputs ? currentNode.outputs[0].links : []) || [];
    //         if (outputs.length) {
    //           for (const linkId of outputs) {
    //             const link = app.graph.links[linkId];
    //             // When disconnecting sometimes the link is still registered
    //             if (!link) continue;
    //             const node = app.graph.getNodeById(link.target_id);
    //             const type = node.constructor.type;
    //             if (type === "Better Reroute") {
    //               // Follow reroute nodes
    //               nodes.push(node);
    //               updateNodes.push(node);
    //             } else {
    //               // We've found an output
    //               const nodeOutType =
    //                 node.inputs &&
    //                 node.inputs[link?.target_slot] &&
    //                 node.inputs[link.target_slot].type
    //                   ? node.inputs[link.target_slot].type
    //                   : null;
    //               if (
    //                 inputType &&
    //                 inputType !== "*" &&
    //                 nodeOutType !== inputType
    //               ) {
    //                 // The output doesnt match our input so disconnect it
    //                 node.disconnectInput(link.target_slot);
    //               } else {
    //                 outputType = nodeOutType;
    //               }
    //             }
    //           }
    //         } else {
    //           // No more outputs for this path
    //         }
    //       }
    //       const displayType = inputType || outputType || "*";
    //       const color = LGraphCanvas.link_type_colors[displayType];
    //       let widgetConfig;
    //       let targetWidget;
    //       let widgetType;
    //       // Update the types of each node
    //       for (const node of updateNodes) {
    //         // If we dont have an input type we are always wildcard but we'll show the output type
    //         // This lets you change the output link to a different type and all nodes will update
    //         node.outputs[0].type = inputType || "*";
    //         node.__outputType = displayType;
    //         node.outputs[0].name = node.properties.showOutputText
    //           ? displayType
    //           : "";
    //         node.size = node.computeSize();
    //         node.applyOrientation();
    //         for (const l of node.outputs[0].links || []) {
    //           const link = app.graph.links[l];
    //           if (link) {
    //             link.color = color;
    //             if (app.configuringGraph) continue;
    //             const targetNode = app.graph.getNodeById(link.target_id);
    //             const targetInput = targetNode.inputs?.[link.target_slot];
    //             if (targetInput?.widget) {
    //               const config = getWidgetConfig(targetInput);
    //               if (!widgetConfig) {
    //                 widgetConfig = config[1] ?? {};
    //                 widgetType = config[0];
    //               }
    //               if (!targetWidget) {
    //                 targetWidget = targetNode.widgets?.find(
    //                   (w) => w.name === targetInput.widget.name
    //                 );
    //               }
    //               const merged = mergeIfValid(targetInput, [
    //                 config[0],
    //                 widgetConfig,
    //               ]);
    //               if (merged.customConfig) {
    //                 widgetConfig = merged.customConfig;
    //               }
    //             }
    //           }
    //         }
    //       }
    //       for (const node of updateNodes) {
    //         if (widgetConfig && outputType) {
    //           node.inputs[0].widget = { name: "value" };
    //           setWidgetConfig(
    //             node.inputs[0],
    //             [widgetType ?? displayType, widgetConfig],
    //             targetWidget
    //           );
    //         } else {
    //           setWidgetConfig(node.inputs[0], null);
    //         }
    //       }
    //       if (inputNode) {
    //         const link = app.graph.links[inputNode.inputs[0].link];
    //         if (link) {
    //           link.color = color;
    //         }
    //       }
    //     };
    //     this.clone = function () {
    //       const cloned = BetterRerouteNode.prototype.clone.apply(this);
    //       cloned.removeOutput(0);
    //       cloned.addOutput(this.properties.showOutputText ? "*" : "", "*");
    //       cloned.size = cloned.computeSize();
    //       return cloned;
    //     };
    //     // This node is purely frontend and does not impact the resulting prompt so should not be serialized
    //     this.isVirtualNode = true;
    //   }
    //   getExtraMenuOptions(_, options) {
    //     options.unshift(
    //       {
    //         content:
    //           (this.properties.showOutputText ? "Hide" : "Show") + " Type",
    //         callback: () => {
    //           this.properties.showOutputText = !this.properties.showOutputText;
    //           if (this.properties.showOutputText) {
    //             this.outputs[0].name =
    //               this.__outputType || this.outputs[0].type;
    //           } else {
    //             this.outputs[0].name = "";
    //           }
    //           this.size = this.computeSize();
    //           this.applyOrientation();
    //           app.graph.setDirtyCanvas(true, true);
    //         },
    //       },
    //       {
    //         content:
    //           (BetterRerouteNode.defaultVisibility ? "Hide" : "Show") +
    //           " Type By Default",
    //         callback: () => {
    //           BetterRerouteNode.setDefaultTextVisibility(
    //             !BetterRerouteNode.defaultVisibility
    //           );
    //         },
    //       },
    //       {
    //         // naming is inverted with respect to LiteGraphNode.horizontal
    //         // LiteGraphNode.horizontal == true means that
    //         // each slot in the inputs and outputs are layed out horizontally,
    //         // which is the opposite of the visual orientation of the inputs and outputs as a node
    //         content:
    //           "Set " + (this.properties.horizontal ? "Horizontal" : "Vertical"),
    //         callback: () => {
    //           this.properties.horizontal = !this.properties.horizontal;
    //           this.applyOrientation();
    //         },
    //       }
    //     );
    //   }
    //   applyOrientation() {
    //     this.horizontal = this.properties.horizontal;
    //     if (this.horizontal) {
    //       // we correct the input position, because LiteGraphNode.horizontal
    //       // doesn't account for title presence
    //       // which reroute nodes don't have
    //       this.inputs[0].pos = [this.size[0] / 2, 0];
    //     } else {
    //       delete this.inputs[0].pos;
    //     }
    //     app.graph.setDirtyCanvas(true, true);
    //   }
    //   computeSize() {
    //     return [
    //       this.properties.showOutputText && this.outputs && this.outputs.length
    //         ? Math.max(
    //             75,
    //             LiteGraph.NODE_TEXT_SIZE * this.outputs[0].name.length * 0.6 +
    //               40
    //           )
    //         : 75,
    //       26,
    //     ];
    //   }
    //   static setDefaultTextVisibility(visible) {
    //     BetterRerouteNode.defaultVisibility = visible;
    //     if (visible) {
    //       localStorage["MLTask.BetterRerouteNode.DefaultVisibility"] = "true";
    //     } else {
    //       delete localStorage["MLTask.BetterRerouteNode.DefaultVisibility"];
    //     }
    //   }
    // }
    // // Load default visibility
    // BetterRerouteNode.setDefaultTextVisibility(
    //   !!localStorage["MLTask.BetterRerouteNode.DefaultVisibility"]
    // );
    // LiteGraph.registerNodeType(
    //   "Better Reroute",
    //   Object.assign(BetterRerouteNode, {
    //     title_mode: LiteGraph.NO_TITLE,
    //     title: "Better Reroute",
    //     collapsable: false,
    //   })
    // );
    // BetterRerouteNode.category = "MLTask/Utils";
  },

  async beforeRegisterNodeDef(nodeType, nodeData, app) {
    // if (nodeData?.input?.optional?.thumbnail?.[1]?.is_url === true) {
    //   nodeData.input.optional.is_url = ["STRING_URL"];
    // }
    if (nodeData?.input?.optional?.thumbnail?.[1]?.image_show === true) {
      nodeData.input.optional.thumbnail__IU = ["BETTER_IMAGE_UPLOAD"];
    }
    if (nodeData?.input?.optional?.yt_thumbnail?.[1]?.image_show === true) {
      nodeData.input.optional.yt_thumbnail__IU = ["BETTER_IMAGE_UPLOAD"];
    }
    if (nodeData?.input?.optional?.fb_thumbnail?.[1]?.image_show === true) {
      nodeData.input.optional.fb_thumbnail__IU = ["BETTER_IMAGE_UPLOAD"];
    }
    if (nodeData?.input?.optional?.insta_thumbnail?.[1]?.image_show === true) {
      nodeData.input.optional.insta_thumbnail__IU = ["BETTER_IMAGE_UPLOAD"];
    }
    if (nodeData?.input?.optional?.pin_thumbnail?.[1]?.image_show === true) {
      nodeData.input.optional.pin_thumbnail__IU = ["BETTER_IMAGE_UPLOAD"];
    }
    switch (nodeData.name) {
      case "SocialManPoster": {
        api.addEventListener(
          "comfyui.socialman.status.update",
          async ({ detail }) => {
            show_message(detail["status"]);
            console.log(detail["status"]);
          }
        );
        api.addEventListener(
          "comfyui.socialman.success",
          async ({ detail }) => {
            show_message(
              `Posted 🎉🎉🎉, <a style="color: yellow;" target="_blank" href="//${detail["link"]}">see post on socialman</a>`
            );
          }
        );

        api.addEventListener("comfyui.socialman.error", async ({ detail }) => {
          let defaultAnchor = `<a style="color: yellow;" target="_blank" href="https://mltask.com/user/comfyui">create a new token</a>`;
          let subscribeAnchor = `<a style="color: yellow;" target="_blank" href="https://mltask.com/pricing">Subscribe On SocialMan</a>`;

          let customErrorMessage = `please make sure you set the token, and the password correctly, if you forgot the password ${defaultAnchor}`;
          const { customError } = detail;

          if (customError == "user_not_subscribed")
            customErrorMessage = `You are not subscribed: please subscribe to complete this post, ${subscribeAnchor}`;

          if (customError == "no_token")
            customErrorMessage = `No token provided: please make sure you set the token, and the password correctly ${defaultAnchor}`;

          if (customError == "invalid_token")
            customErrorMessage = `Invalid token: ${customErrorMessage}`;

          if (customError == "bad_token")
            customErrorMessage = `Bad token: please make sure you set the token, ${defaultAnchor}`;

          if (customError == "token_revoked")
            customErrorMessage = `Token revoked: ${defaultAnchor}`;

          if (customError == "token_expired")
            customErrorMessage = `Token expired: ${defaultAnchor}`;

          if (customError == "wrong_password")
            customErrorMessage = `Wrong password: please set the password correctly, if you forgot the password ${defaultAnchor}`;

          if (customError == "no_password_set")
            customErrorMessage = `No password provided: please set the password correctly, if you forgot the password ${defaultAnchor}`;

          show_message(`${customErrorMessage}`);
        });
        api.addEventListener(
          "comfyui.socialman.error.unknown",
          async ({ detail }) => {
            show_message(
              "Whoops! Something went wrong, make sure the video is valid, then please try again later"
            );
          }
        );

        break;
      }

      default: {
        break;
      }
    }
  },
});

//how load image works
//nodes.py
// class LoadImage:
//     @classmethod
//     def INPUT_TYPES(s):
//         input_dir = folder_paths.get_input_directory()
//         files = [f for f in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, f))]
//         return {"required":
//                     {"image": (sorted(files), {"image_upload": True})},
//                 }

//how its widget is made
// web/extensions/core/uploadImage.js
// app.registerExtension({
// 	name: "Comfy.UploadImage",
// 	async beforeRegisterNodeDef(nodeType, nodeData, app) {
// 		if (nodeData?.input?.required?.image?.[1]?.image_upload === true) {
// 			nodeData.input.required.upload = ["IMAGEUPLOAD"];
//       //see other input types here web/scripts/widgets.js
// 		}
// 	},
// });
