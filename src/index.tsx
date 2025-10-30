import {
  ButtonItem,
  PanelSection,
  PanelSectionRow,
  staticClasses
} from "@decky/ui";
import {
  callable,
  definePlugin,
  toaster,
} from "@decky/api"
import { MdDesktopMac } from "react-icons/md";

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
        
        if (artwork.grid) {
          SteamClient.Apps.SetCustomArtworkForApp(shortcutId, artwork.grid, "jpg", 0);
        }
        if (artwork.hero) {
          SteamClient.Apps.SetCustomArtworkForApp(shortcutId, artwork.hero, "jpg", 1);
        }
        if (artwork.logo) {
          SteamClient.Apps.SetCustomArtworkForApp(shortcutId, artwork.logo, "png", 2);
        }
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
      const appOverview = appStore.GetAppOverviewByAppID(shortcutId);
      if (!appOverview) {
        toaster.toast({
          title: "Error",
          body: "Shortcut not found. Please create it first or restart Steam."
        });
        return;
      }

      // Launch via Steam's game running system
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
    <PanelSection title="Nested Desktop">
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
    </PanelSection>
  );
};

export default definePlugin(() => {
  return {
    name: "Nested Desktop",
    titleView: <div className={staticClasses.Title}>Nested Desktop</div>,
    content: <Content />,
    icon: <MdDesktopMac />,
  };
});
