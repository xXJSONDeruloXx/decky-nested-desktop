import {
  ButtonItem,
  PanelSection,
  PanelSectionRow,
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
import { FaShip } from "react-icons/fa";

// import logo from "../assets/logo.png";

// Get or create the shortcut ID for nested desktop
const createNestedDesktopShortcut = callable<[], any>("create_nested_desktop_shortcut");
const launchNestedDesktopShortcut = callable<[], any>("launch_nested_desktop_shortcut");
const saveNestedDesktopShortcutId = callable<[shortcutId: number], boolean>("save_nested_desktop_shortcut_id");
const getNestedDesktopArtwork = callable<[], any>("get_nested_desktop_artwork");

function Content() {
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

      // Get and apply artwork
      const artworkResult = await getNestedDesktopArtwork();
      if (artworkResult.success && artworkResult.artwork) {
        const artwork = artworkResult.artwork;
        
        // Apply artwork using SteamClient API
        // Types: 0 = Grid (vertical), 1 = Hero (wide banner), 2 = Logo, 3 = GridH (horizontal)
        // @ts-ignore - SteamClient is available at runtime
        if (artwork.grid) {
          SteamClient.Apps.SetCustomArtworkForApp(shortcutId, artwork.grid, "jpg", 0);
        }
        // @ts-ignore
        if (artwork.hero) {
          SteamClient.Apps.SetCustomArtworkForApp(shortcutId, artwork.hero, "jpg", 1);
        }
        // @ts-ignore
        if (artwork.logo) {
          SteamClient.Apps.SetCustomArtworkForApp(shortcutId, artwork.logo, "png", 2);
        }
        // @ts-ignore
        if (artwork.gridH) {
          SteamClient.Apps.SetCustomArtworkForApp(shortcutId, artwork.gridH, "jpg", 3);
        }
      }

      toaster.toast({
        title: "Success",
        body: "Nested Desktop shortcut created with artwork!"
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
