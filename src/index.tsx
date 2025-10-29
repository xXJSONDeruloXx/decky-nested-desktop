import {
  ButtonItem,
  PanelSection,
  PanelSectionRow,
  Navigation,
  staticClasses
} from "@decky/ui";
import {
  addEventListener,
  removeEventListener,
  callable,
  definePlugin,
  toaster,
  // routerHook
} from "@decky/api"
import { useState } from "react";
import { FaShip } from "react-icons/fa";

// import logo from "../assets/logo.png";

// This function calls the python function "add", which takes in two numbers and returns their sum (as a number)
// Note the type annotations:
//  the first one: [first: number, second: number] is for the arguments
//  the second one: number is for the return value
const add = callable<[first: number, second: number], number>("add");

// This function calls the python function "start_timer", which takes in no arguments and returns nothing.
// It starts a (python) timer which eventually emits the event 'timer_event'
const startTimer = callable<[], void>("start_timer");

// Get or create the shortcut ID for nested desktop
const createNestedDesktopShortcut = callable<[], any>("create_nested_desktop_shortcut");
const launchNestedDesktopShortcut = callable<[], any>("launch_nested_desktop_shortcut");
const saveNestedDesktopShortcutId = callable<[shortcutId: number], boolean>("save_nested_desktop_shortcut_id");

function Content() {
  const [result, setResult] = useState<number | undefined>();

  const onClick = async () => {
    const result = await add(Math.random(), Math.random());
    setResult(result);
  };

  const createShortcut = async () => {
    try {
      const result = await createNestedDesktopShortcut();
      
      if (!result.success) {
        toaster.toast({
          title: "Error",
          body: result.message || "Failed to create shortcut"
        });
        return;
      }

      // Create the shortcut using Steam's API
      // @ts-ignore - SteamClient is available at runtime
      const shortcutId = await SteamClient.Apps.AddShortcut(
        result.name,
        result.desktop_file,
        result.desktop_file,
        ""
      );
      
      if (shortcutId <= 0) {
        toaster.toast({
          title: "Error",
          body: "Failed to create Steam shortcut"
        });
        return;
      }

      // Save the shortcut ID for later use
      await saveNestedDesktopShortcutId(shortcutId);

      toaster.toast({
        title: "Success",
        body: "Nested Desktop shortcut created!"
      });
    } catch (error) {
      toaster.toast({
        title: "Error",
        body: String(error)
      });
    }
  };

  const launchShortcut = async () => {
    try {
      const result = await launchNestedDesktopShortcut();
      
      if (!result.success) {
        toaster.toast({
          title: "Error",
          body: result.message || "Failed to launch"
        });
        return;
      }

      // Get the shortcut ID from the backend
      const shortcutId = result.shortcut_id;
      
      // Get the game ID from the app ID
      // @ts-ignore - appStore is available at runtime
      const appOverview = appStore.GetAppOverviewByAppID(shortcutId);
      if (!appOverview) {
        toaster.toast({
          title: "Error",
          body: "Shortcut not found. Please create it first or restart Steam."
        });
        return;
      }

      // Launch via Steam's game running system
      // @ts-ignore - SteamClient is available at runtime
      SteamClient.Apps.RunGame(appOverview.m_gameid, "", -1, 100);
      
      toaster.toast({
        title: "Nested Desktop",
        body: "Launching..."
      });
    } catch (error) {
      toaster.toast({
        title: "Error",
        body: String(error)
      });
    }
  };

  return (
    <PanelSection title="Panel Section">
      <PanelSectionRow>
        <ButtonItem
          layout="below"
          onClick={onClick}
        >
          {result ?? "Add two numbers via Python"}
        </ButtonItem>
      </PanelSectionRow>
      <PanelSectionRow>
        <ButtonItem
          layout="below"
          onClick={() => startTimer()}
        >
          {"Start Python timer"}
        </ButtonItem>
      </PanelSectionRow>

      <PanelSectionRow>
        <ButtonItem
          layout="below"
          onClick={createShortcut}
        >
          {"Create Nested Desktop Shortcut"}
        </ButtonItem>
      </PanelSectionRow>

      <PanelSectionRow>
        <ButtonItem
          layout="below"
          onClick={launchShortcut}
        >
          {"Launch Nested Desktop"}
        </ButtonItem>
      </PanelSectionRow>

      {/* <PanelSectionRow>
        <div style={{ display: "flex", justifyContent: "center" }}>
          <img src={logo} />
        </div>
      </PanelSectionRow> */}

      {/*<PanelSectionRow>
        <ButtonItem
          layout="below"
          onClick={() => {
            Navigation.Navigate("/decky-plugin-test");
            Navigation.CloseSideMenus();
          }}
        >
          Router
        </ButtonItem>
      </PanelSectionRow>*/}
    </PanelSection>
  );
};

export default definePlugin(() => {
  console.log("Template plugin initializing, this is called once on frontend startup")

  // serverApi.routerHook.addRoute("/decky-plugin-test", DeckyPluginRouterTest, {
  //   exact: true,
  // });

  // Add an event listener to the "timer_event" event from the backend
  const listener = addEventListener<[
    test1: string,
    test2: boolean,
    test3: number
  ]>("timer_event", (test1, test2, test3) => {
    console.log("Template got timer_event with:", test1, test2, test3)
    toaster.toast({
      title: "template got timer_event",
      body: `${test1}, ${test2}, ${test3}`
    });
  });

  return {
    // The name shown in various decky menus
    name: "Test Plugin",
    // The element displayed at the top of your plugin's menu
    titleView: <div className={staticClasses.Title}>Decky Example Plugin</div>,
    // The content of your plugin's menu
    content: <Content />,
    // The icon displayed in the plugin list
    icon: <FaShip />,
    // The function triggered when your plugin unloads
    onDismount() {
      console.log("Unloading")
      removeEventListener("timer_event", listener);
      // serverApi.routerHook.removeRoute("/decky-plugin-test");
    },
  };
});
