
//  AppDelegate.m
//  SyncBT Client

/*
 
 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.
 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.
 You should have received a copy of the GNU General Public License
 along with this program.  If not, see <http://www.gnu.org/licenses/>.
 
 For further questions related to the SyncBlue development, feel free to contact us at syncblueapp@gmail.com
 
 
 */

// Import libraries and frameworks
#import <Cocoa/Cocoa.h>
#import "AppDelegate.h"

// Import MultipeerConnectivity framework
#import <MultipeerConnectivity/MultipeerConnectivity.h>

// IOBluetooth Framework
#include <IOBluetooth/OBEXBluetooth.h>
#import <IOBluetooth/Bluetooth.h>
#import <IOBluetooth/IOBluetoothUserLib.h>
#import <IOBluetooth/IOBluetoothUtilities.h>
#import <IOBluetooth/IOBluetoothUserLib.h>

#import <IOBluetooth/objc/OBEXSession.h>
#import <IOBluetooth/objc/IOBluetoothSDPUUID.h>
#import <IOBluetooth/objc/IOBluetoothDevice.h>
#import <IOBluetooth/objc/IOBluetoothDeviceInquiry.h>
#import <IOBluetooth/objc/IOBluetoothSDPDataElement.h>
#import <IOBluetooth/objc/OBEXFileTransferServices.h>
#import <IOBluetooth/objc/IOBluetoothOBEXSession.h>

// IOBluetoothUI Framework
#import <IOBluetoothUI/IOBluetoothUIUserLib.h>
#import <IOBluetooth/objc/IOBluetoothSDPServiceRecord.h>
#import <IOBluetoothUI/objc/IOBluetoothDeviceSelectorController.h>
#import <IOBluetoothUI/objc/IOBluetoothServiceBrowserController.h>

// Define Functions
#define	DEBUG_NAME	"[SynceBTClientDebug]"
#define Log( FMT, ARGS... )		NSLog(@ FMT, ## ARGS )

int ListingValuesSorter( id	object1, id object2, void* theContext );
enum {
    kTestTypeOOP	= 1,
    kTestTypeFTP	= 2
};

@implementation AppDelegate

@synthesize mOPPProgressIndicator;

- (void)awakeFromNib {
    [[connectButton window] center];
    [[connectButton window] performSelector:@selector(makeFirstResponder:)
                                 withObject:connectButton
                                 afterDelay:0.0];
    
    [self.mOPPProgressIndicator		setIndeterminate: FALSE];
    [mOPPFileStatusField		setStringValue: @""];
    [mOPPFileTransferredField	setStringValue: @""];
    [mOPPFileRemainingField		setStringValue: @"" ];
    
}

- (void) applicationWillFinishLaunching:(NSNotification *)notification;
{
    if ( IOBluetoothValidateHardware( nil ) != kIOReturnSuccess )
    {
        [NSApp terminate:self];
    }
}

//----------------------------------------------------------------------------------------------------

#pragma mark Other Actions

- (void)dealloc {

    [super dealloc];
    
}

- (void)resetButtons {
    nil;
}

- (IBAction)clear:(id)sender {
    
    [logTextView setString: @" "];
    
}

- (void)log:(NSString *)text {
    [logTextView insertText:text];
    [logTextView insertText:@"\n"];
}

- (NSNumber *)getSizeOfFile:(NSString *)filePath {
    NSFileManager *fileManager = [NSFileManager defaultManager];
    NSDictionary *fileAttributes = [fileManager fileAttributesAtPath:filePath traverseLink:YES];
    if (fileAttributes != nil)
        return [fileAttributes objectForKey:NSFileSize];
    return nil;
}

-(NSString *)getNameOfDevice {
    
    NSString *deviceNameAsAString = [device getName];
    
    return deviceNameAsAString;
}

- (IBAction)createFolder:(id)sender {

    [mTransferServices createFolder:@"Folder"];
    
}

- (IBAction)openBrowserInterface:(id)sender {
    
    [mBrowserInterface makeKeyAndOrderFront:nil];
    
}

- (IBAction)closeBrowserInterface:(id)sender {
    
    [mBrowserInterface close];
    //[mBrowserInterface release];
    
}

//----------------------------------------------------------------------------------------------------
#pragma mark Browser functions

- (IBAction)connectToFTP:(id)sender {
    
    [mOBEXSession release];
    mOBEXSession = nil;
    
    [self connect];
    
}

- (IBAction) getFileFTP:(id)sender {
    NSSavePanel *	savePanel		= nil;
    NSString *		dir				= nil;
    NSString *		file			= nil;
    int				row;
    
    if( ! mTransferServices || [mTransferServices isConnected] == FALSE )
    {
        Log("[get] ERR: no connection!\n");
        goto exit;
    }
    
    if( !mFTPCurrentDirectoryObjects )
    {
        Log("[get] ERR: no directory items!\n");
        goto exit;
    }
    
    row = [mFTPBrowseTable selectedRow];
    if( row < 0 || row >= [mFTPCurrentDirectoryObjects count] )
    {
        Log("[get] ERR: bad selection\n");
        goto exit;
    }
    
    savePanel = [NSSavePanel savePanel];
    if( !savePanel )
    {
        Log("[get] ERR: No save panel\n");
        goto exit;
    }
    
    file = [[mFTPCurrentDirectoryObjects objectAtIndex:row] objectForKey:@"name"];
    
    [savePanel beginSheetForDirectory: dir
                                 file: file
                       modalForWindow: mMainWindow
                        modalDelegate: self
                       didEndSelector: @selector( getFTPPanelDidEnd:returnCode:contextInfo: )
                          contextInfo: self];
exit:
    Log("[get] exit\n");
    return;
}

- (IBAction)removeItem:(id)sender {
    
    NSString *		file			= nil;
    int				row;
    
    if( ! mTransferServices || [mTransferServices isConnected] == FALSE )
    {
        Log("[get] ERR: no connection!\n");
        goto exit;
    }
    
    if( !mFTPCurrentDirectoryObjects )
    {
        Log("[get] ERR: no directory items!\n");
        goto exit;
    }
    
    row = [mFTPBrowseTable selectedRow];
    if( row >= [mFTPCurrentDirectoryObjects count] )
    {
        Log("[get] ERR: bad selection\n");
        goto exit;
    }
    
    // Select the file to remove
    
    file = [[mFTPCurrentDirectoryObjects objectAtIndex:row] objectForKey:@"name"];
    
    NSTableColumn *column = [mFTPBrowseTable tableColumnWithIdentifier:@"size"];
    NSCell *cell = [column dataCellForRow:row];
    
    NSLog(@"cell value:%@", [cell stringValue]);
    NSLog(@"File selected to remove:%@", file);
    
    // Tell OBEX to remove the item
    
    if ([[cell stringValue] isEqual:@"-folder-"]) {
        
        [self removeFolder];
        
    }
    
    else {
    
    [mTransferServices removeItem:file];
        
    }
    
    // Listing files again
    
    [mTransferServices retrieveFolderListing];
    
exit:
    Log("[get] exit\n");
    return;
    
    
}

- (void)removeFolder {
    
    NSLog(@"Folder");
    
    NSString *		file			= nil;
    int				row;
    
    row = [mFTPBrowseTable selectedRow];
    file = [[mFTPCurrentDirectoryObjects objectAtIndex:row] objectForKey:@"name"];
    [mTransferServices removeItem:file];

}

- (IBAction)sendFileFTP:(id)sender {
    NSOpenPanel	* openPanel = nil;
    
    if( ! mTransferServices || [mTransferServices isConnected] == FALSE )
    {
        Log("[send] ERR: no connection!\n");
        return;
    }
    
    openPanel = [NSOpenPanel openPanel];
    if( !openPanel ){ return; }
    
    [openPanel	setAllowsMultipleSelection:FALSE];
    [openPanel	setCanChooseFiles:TRUE];
    [openPanel	setCanChooseDirectories:YES];
    [openPanel	setPrompt:@"Send"];
    
    [openPanel beginSheetForDirectory: nil
                                 file: nil
                                types: nil
                       modalForWindow: mMainWindow
                        modalDelegate: self
                       didEndSelector: @selector( sendFTPPanelDidEnd:returnCode:contextInfo: )
                          contextInfo: self];
    
    [self log:@"Sending file in progress..."];

}

- (IBAction)sendDataFTP:(id)sender {
    NSOpenPanel	* openPanel = nil;
    
    if( ! mTransferServices || [mTransferServices isConnected] == FALSE )
    {
        Log("[send] ERR: no connection!\n");
        return;
    }
    
    openPanel = [NSOpenPanel openPanel];
    if( !openPanel ){ return; }
    
    [openPanel	setAllowsMultipleSelection:FALSE];
    [openPanel	setCanChooseFiles:TRUE];
    [openPanel	setCanChooseDirectories:YES];
    [openPanel	setPrompt:@"Send"];
    
    [openPanel beginSheetForDirectory: nil
                                 file: nil
                                types: nil
                       modalForWindow: mMainWindow
                        modalDelegate: self
                       didEndSelector: @selector( sendDataPanelDidEnd:returnCode:contextInfo: )
                          contextInfo: self];
    
    [self log:@"Sending file in progress..."];
    
    [mTransferServices changeCurrentFolderForwardToPath:[mTransferServices currentPath]];
    
}


- (IBAction)setPathAction:(id)sender {
    
    NSString *		inPath			= nil;
    int				row;
    
    if( ! mTransferServices || [mTransferServices isConnected] == FALSE )
    {
        Log("[setPathAction] ERR: no connection!\n");
        goto exit;
    }
    
    if( !mFTPCurrentDirectoryObjects )
    {
        Log("[setPathAction] ERR: no directory items!\n");
        goto exit;
    }
    
    row = [mFTPBrowseTable selectedRow];
    if( row == -1 )
    {
        Log("[setPathAction] ERR: bad selection\n");
        
        goto exit;
        
    }
    
    //[self log:[NSString stringWithFormat: @"Row: %d", row]];
    
    // Set the new directory as the name of the selected row
    
    inPath = [[mFTPCurrentDirectoryObjects objectAtIndex:row] objectForKey:@"name"];
    
    [mTransferServices changeCurrentFolderForwardToPath:inPath];
    
exit:
    Log("[get] exit\n");
    return;
    
}

- (IBAction)upDirectory:(id)sender {
    
    // Check if everything is working correctly before sending a request to change directory through OBEX
    
    // Make sure that OBEX service is running correctly
    if( ! mTransferServices || [mTransferServices isConnected] == FALSE )
    {
        Log("[get] ERR: no connection!\n");
        goto exit;
    }
    
    // Launch the action through OBEX
    [mTransferServices changeCurrentFolderBackward];
    
exit:
    Log("[get] exit\n");
    return;
    
}

- (IBAction)homeDirectory:(id)sender {
    
    // Check if everything is working correctly before sending a request to change directory through OBEX
    
    // Make sure that OBEX service is running correctly
    if( ! mTransferServices || [mTransferServices isConnected] == FALSE )
    {
        Log("[get] ERR: no connection!\n");
        goto exit;
    }

    // Launch the action through OBEX
    [mTransferServices changeCurrentFolderToRoot];
    
exit:
    Log("[get] exit\n");
    return;
    
}


- (void) connect {
    
    IOBluetoothDeviceSelectorController *	deviceSelector;
    NSArray *								devicesArray;
    IOBluetoothSDPServiceRecord *			record;
    
    Log("[connect] entry\n");
    
    // Get browser to get a service ref.
    deviceSelector = [IOBluetoothDeviceSelectorController deviceSelector];
    if(!deviceSelector)
    {
        Log("[connect] Err: no device selector\n");
        goto exit;
    }
    
    //
    //  FILE TRANSFER
    //
    
    [deviceSelector addAllowedUUID: [IOBluetoothSDPUUID uuid16:kBluetoothSDPUUID16ServiceClassOBEXFileTransfer]];
    [deviceSelector setTitle: @"Browse"];
    [deviceSelector setPrompt: @"Browse"];
    [deviceSelector setDescriptionText: @"Select a device to browse"];
    
    // run the panel
    [deviceSelector setSearchAttributes:0];
    [deviceSelector	runModal];
    
    /*if ( [deviceSelector runModal] != kIOBluetoothUISuccess )
     {
     NSLog( @"User has cancelled the device selection.\n" );
     goto exit;
     }
     */
    
    devicesArray = [deviceSelector getResults];
    if( !devicesArray )
    {
        Log("[connect] ERR: no device array\n");
        goto exit;
    }
    
    // get the selected device
    device = [devicesArray objectAtIndex:0];
    if( !device )
    {
        Log("[connect] ERR: no device\n");
        goto exit;
    }
    
    //  Get the service record of the service we want to use
    
    record = [device getServiceRecordForUUID:[IOBluetoothSDPUUID uuid16:kBluetoothSDPUUID16ServiceClassOBEXFileTransfer]];
    
    //  Use the record to form an OBEX Session object
    
    mOBEXSession = [IOBluetoothOBEXSession withSDPServiceRecord: record];
    [mOBEXSession retain];
    
    //  Send the OBEXSession off to FTS
    
    mTransferServices = [OBEXFileTransferServices withOBEXSession: mOBEXSession];
    [mTransferServices retain];
    [mTransferServices setDelegate: self];
    [mTransferServices connectToFTPService];

    //Get the device address string connected to as a string
    
    NSString *deviceAddressString = [device getAddressString];
    
    [addressField setStringValue:deviceAddressString];
    
    //Specify the name of the device
    
    NSString *deviceNameAsAString = [device getName];
    
    NSString *outputText = [NSString stringWithFormat:@"Device %@ is connected",
                            deviceNameAsAString];
    
    //Get the rfCOMM channel connected to
    UInt8	rfcommChannelID;
    [record getRFCOMMChannelID:&rfcommChannelID];
    
    int *channelConnected = rfcommChannelID;
    
    [channelField setIntValue:channelConnected];
    
    [connectionLog setStringValue:outputText];
    
    [self log:[NSString stringWithFormat:@"Connected to device with name %@ with Bluetooth address %@ on channel %d",
               deviceNameAsAString, deviceAddressString,[channelField intValue]]];
    
    //Open the Browser Interface
    
    [mBrowserInterface makeKeyAndOrderFront:self];
    
    // Update the UI buttons
    
    [browseDeviceButton setEnabled:YES];
    [mFTPConnectButton setTitle:	@"Disconnect"];
    [mFTPConnectButton setAction:	@selector(abortAction:)];
    
    //  Connect to the service we specified when we did our device discovery
    
    [mTransferServices connectToFTPService];
    
exit:
    
    Log("[connect] exit\n");
    
    return;
    
}

- (void) abortAction:(id)sender {
    
    Log("Aborting...\n");
    
    if( mTransferServices && [mTransferServices isConnected] ) {
        
        [mTransferServices disconnect];
        
    }
    
    [mTransferServices disconnect];
    
}

- (IBAction) quit:(id)sender {
    Log("Time to terminate.....\n");
    
    [NSApp terminate:self];
}

- (void) getFTPPanelDidEnd:(NSSavePanel *)sheet returnCode:(int)returnCode contextInfo:(void *)contextInfo {
    NSString *			chosenPath	= nil;
    NSString *			fileName	= nil;
    BOOL				conflict	= YES;
    NSFileManager *		fm			= nil;
    int					row;
    
    Log("[getFTPPanelDidEnd] entry.  Return: %d\n", returnCode );
    
    // Did they cancel?
    
    if( returnCode == NSCancelButton )
    {
        return;
    }
    
    conflict = FALSE;
    fm = [NSFileManager defaultManager];
    
    chosenPath = [sheet filename];
    Log("Final path: %s\n", [chosenPath UTF8String] );
    
    
    row = [mFTPBrowseTable selectedRow];
    if( row < 0 || row  >= [mFTPCurrentDirectoryObjects count] )
    {
        return;
    }
    
    fileName = [[mFTPCurrentDirectoryObjects objectAtIndex: row] objectForKey: @"name"];
    
    if( [fm fileExistsAtPath:chosenPath] )
    {
        int res;
        
        res = NSRunAlertPanel( @"Save",
                              [NSString stringWithFormat:@"Selected files already exist at %@.  Replace them?", chosenPath],
                              @"Replace",
                              @"Cancel",
                              nil);
        
        if( res == NSAlertDefaultReturn )
        {
            [mTransferServices copyRemoteFile: fileName
                                  toLocalPath: chosenPath];
        }
    }
    else
    {
        [mTransferServices copyRemoteFile: fileName
                              toLocalPath: chosenPath];
    }
}

- (void) sendFTPPanelDidEnd:(NSOpenPanel *)sheet returnCode:(int)returnCode contextInfo:(void *)contextInfo {
    
    // Did they cancel?
    
    if( returnCode == NSCancelButton ){ return; }
    
    // Take the file selected
    
    mFileToSend = [[sheet filenames] lastObject];
    
    // Take the file size
    
    mFileSizeToSend = [self getSizeOfFile:mFileToSend];
    
    NSString *currentPath = [mTransferServices currentPath];
        
    [mTransferServices sendFile: mFileToSend];
    
    [self log:[NSString stringWithFormat:@"Sending file <%@> of size: %d in path %@",mFileToSend,
               [mFileSizeToSend unsignedIntValue], currentPath]];
    
}

- (void) fileTransferServicesConnectionComplete: (OBEXFileTransferServices*)inServices
                                          error: (OBEXError)inError
{
    Log("[CONNECT_Function]  entry - status: %d\n", inError);
    
    switch( inError )
    {
        case( kOBEXSuccess ):
        {
            if( mTestType == kTestTypeOOP )
            {
                [mOPPProgressIndicator	setIndeterminate: TRUE];
                [mOPPProgressIndicator	startAnimation: self];
                [mOPPFileStatusField	setStringValue: @"Waiting for response..."];
                
                [mTransferServices sendFile: mOPPSelectedFile];
            }
            else
            {
                [mTransferServices changeCurrentFolderToRoot];
            }
            
            break;
        }
            
        default:
        {
            Log("[CONNECT_Function]  We had an error: %d\n", inError );	
            break;
        }
    }
}


- (void) fileTransferServicesDisconnectionComplete: (OBEXFileTransferServices*)inServices
                                             error: (OBEXError)inError
{
    Log("[DISCONNECT_FUNCTION]  entry - err: %d\n", inError);
    
    switch( inError )
    {
        case( kOBEXSuccess ):
        {
            break;
        }
            
        case( kOBEXTimeoutError ):
        {
            Log("[DISCONNECT_FUNCTION] ERR: Time-out\n");
            break;
        }
            
        case( kOBEXSessionTransportDiedError ):
        case( kOBEXSessionNoTransportError ):
        case( kOBEXSessionNotConnectedError ):
        {
            Log("[DISCONNECT_FUNCTION] ERR: Transport %d\n", inError );
            break;
        }
            
        default:
        {
            Log("[DISCONNECT_FUNCTION] Defaulted: %d\n", inError );
            break;
        }
    }
    
    NSLog(@"Connected to FTP action");
    
    [self log:[NSString stringWithFormat: @"Disconnected from %@ with success", [device getName]]];
    
    [self log:@"Clearing the log area..."];
    
    [self performSelector: @selector(clear:)
     withObject: nil
     afterDelay: 2.0];
    
    [addressField setStringValue:@""];
    [addressField setPlaceholderString:@"Please select Connect"];
    [channelField setStringValue:@""];
    
    [mFTPConnectButton setTitle: @"Connect"];
    [mFTPConnectButton setAction: @selector(connectToFTP:)];
    
    [connectionLog setStringValue:@" "];
    
    [mFTPCurrentDirectoryObjects removeAllObjects];
    [mFTPBrowseTable reloadData];
    
    [mTransferServices release];
    mTransferServices = nil;
    
    [[mOBEXSession getDevice] closeConnection];
    [mOBEXSession release];
    mOBEXSession = nil;
    
    if( inError )
    {
        Log("[DISCONNECT_FUNCTION] We tried to disconnect but junk returned to us.\n");
    }
}


- (void) fileTransferServicesSendFileProgress:(OBEXFileTransferServices*)inServices			transferProgress:(NSDictionary*)inProgress
{
    
    [self.mOPPProgressIndicator	startAnimation:self];

    [self.mOPPProgressIndicator setIndeterminate:NO];
    
    totalLength = [[inProgress objectForKey: (NSString*)kFTSProgressBytesTotalKey] intValue];
    
    bytesSentOutofTotalLength = [[inProgress objectForKey: (NSString*)kFTSProgressBytesTransferredKey] floatValue];

    length = ([[inProgress objectForKey: (NSString*)kFTSProgressBytesTotalKey] intValue] - [[inProgress objectForKey: (NSString*)kFTSProgressBytesTransferredKey] floatValue]);
    
    percentageProgress = [[inProgress objectForKey: (NSString*)kFTSProgressPercentageKey] intValue];
        
    self.mOPPProgressIndicator.doubleValue = percentageProgress;
    
    [mOPPFileTransferredField	setStringValue: [inProgress objectForKey: (NSString*)kFTSProgressTransferRateKey]];
    
    [mOPPFileStatusField		setStringValue: @"Transferring"];
    
    [mOPPFileRemainingField		setFloatValue: ([[inProgress objectForKey: (NSString*)kFTSProgressBytesTotalKey] intValue] - [[inProgress objectForKey: (NSString*)kFTSProgressBytesTransferredKey] floatValue]) ];
    
    [self log:[NSString stringWithFormat:@"File transfer in progress. Bytes sent %d out of %d with %d completed...", bytesSentOutofTotalLength, totalLength, percentageProgress]];

}

- (void) fileTransferServicesSendFileComplete: (OBEXFileTransferServices*) inServices
                                        error: (OBEXError) inError
{
    Log("[PUT_Function] Entry. status = %d\n", inError );
    
    [self.mOPPProgressIndicator stopAnimation:self];
    
    self.mOPPProgressIndicator.doubleValue = 0;
    
    [mTransferServices retrieveFolderListing];
    
    [mOPPProgressIndicator		setIndeterminate: FALSE];
    [mOPPFileStatusField		setStringValue: @"Done"];
    [mOPPFileTransferredField	setStringValue: @""];
    [mOPPFileRemainingField	setStringValue: @"" ];
    
    switch( inError )
    {
        case( kOBEXSuccess ):
        {
            Log("[SendComplete] All done....\n");

            if( mTestType == kTestTypeOOP )
            {
                [mTransferServices disconnect];
            }
            
            break;

        }
            
        case( kOBEXTimeoutError ):
        {
            Log(" [SendComplete] ERR: We've timed out, so lets bail out on those punks\n");
            [self fileTransferServicesDisconnectionComplete: mTransferServices
                                                      error: kOBEXSuccess];
            break;
        }
            
        case( kOBEXCancelledError ):
        case( kOBEXBadRequestError ):
        {
            Log("[SendComplete] ERR: they didn't accept it, bummer\n");
            
            [self fileTransferServicesSendFileComplete: mTransferServices
                                                 error: kOBEXSuccess];
            break;
        }
            
        case( kOBEXGeneralError ):
        {
            Log("[SendComplete] ERR: transfer failed...\n");			
            [self fileTransferServicesDisconnectionComplete: mTransferServices
                                                      error: kOBEXSuccess];
            break;
        }
            
        default:
        {
            Log("[SendComplete] ERR: Defaulted (%d)\n", inError);
            break;
        }
    }
}

- (void) fileTransferServicesCopyRemoteFileProgress:(OBEXFileTransferServices*)inServices			transferProgress:(NSDictionary*)inProgress
{
    Log("[GET_Function]: total:%d  tx:%d  rate:%f\n", [[inProgress objectForKey: (NSString*)kFTSProgressBytesTotalKey] intValue],
        [[inProgress objectForKey: (NSString*)kFTSProgressBytesTransferredKey] intValue],
        [[inProgress objectForKey: (NSString*)kFTSProgressTransferRateKey] floatValue] );
    
    
    [self.mOPPProgressIndicator		setIndeterminate: TRUE];
    [mOPPFileTransferredField	setStringValue: [inProgress objectForKey: (NSString*)kFTSProgressTransferRateKey]];
    [mOPPFileStatusField		setStringValue: @"Transferring"];
    [mOPPFileRemainingField		setFloatValue: ([[inProgress objectForKey: (NSString*)kFTSProgressBytesTotalKey] intValue] - [[inProgress objectForKey: (NSString*)kFTSProgressBytesTransferredKey] floatValue]) ];
}

- (void) fileTransferServicesCopyRemoteFileComplete:(OBEXFileTransferServices*)inServices			error:(OBEXError)inError
{
    [self.mOPPProgressIndicator		setIndeterminate: FALSE];
    [mOPPFileStatusField		setStringValue: @"Done"];
    [mOPPFileTransferredField	setStringValue: @""];
    [mOPPFileRemainingField	setStringValue: @"" ];
    [browseDeviceButton setEnabled:NO];
    
    
    switch( inError )
    {
        case( kOBEXSuccess ):
        {
            Log("[GET_Function] Success\n");
            // [[NSWorkspace sharedWorkspace] noteFileSystemChanged: [NSHomeDirectory() stringByAppendingPathComponent: @"gauntlet-vcard.vcf"]];
            break;
        }
            
        case( kOBEXGeneralError ):
        {
            Log("[GET_Function] ERR: General Error\n");
            break;
        }
            
        case( kOBEXTimeoutError ):
        {
            Log("[GET_Function] ERR: Timed-out\n");
            break;
        }
            
        case( kOBEXBadRequestError ):
        {
            Log("[GET_Function] ERR: Bad Request\n");
            break;
        }
            
        case( kOBEXCancelledError ):
        {
            Log("[GET_Function] ERR: Cancelled\n");
            break;
        }
            
        default:
        {
            Log("[GET_Function] Defaulted: %d\n", inError );
            break;
        }
    }
    
}

- (void) fileTransferServicesAbortComplete: (OBEXFileTransferServices*)inServices
                                     error: (OBEXError)inError
{
    switch( inError )
    {
        case( kOBEXSuccess ):
        {
            Log("[ABORT_Function] Success!\n");
            break;
        }
            
        case( kOBEXTimeoutError ):
        {
            Log("[ABORT_Function] ERR: Timed-out\n");
            break;
        }
            
        default:
        {
            Log("[ABORT_Function] Defaulted: %d\n", inError);
            break;
        }
    }
    
    [mTransferServices disconnect];
}

- (void) fileTransferServicesRetrieveFolderListingComplete: (OBEXFileTransferServices*)inServices
                                                     error: (OBEXError)inError
                                                   listing: (NSArray*)inListing
{
    Log("[LISTING_Function]  entry - err: %d\n", inError );
    
    if( inError == kOBEXSuccess )
    {
        [self listFilesInBrowserFromList: inListing];
        NSString *path = [NSString stringWithFormat:@"%@", [mTransferServices currentPath]];
        NSURL *url = [NSURL fileURLWithPath :path];
        
        [pathController setURL:url];
        [setPathTextField setStringValue:[mTransferServices currentPath]];

    }
    
}

- (void) fileTransferServicesCreateFolderComplete: (OBEXFileTransferServices*)inServices
                                            error: (OBEXError)inError
                                           folder: (NSString*)inFolderName
{
    Log("[CREATE_Function]  entry - status: %d\n", inError);
    
    if( inError == kOBEXSuccess )
    {
        [mTransferServices retrieveFolderListing];
        NSString *path = [NSString stringWithFormat:@"%@", [mTransferServices currentPath]];
        NSURL *url = [NSURL fileURLWithPath :path];
        
        [pathController setURL:url];
        [setPathTextField setStringValue:[mTransferServices currentPath]];

    }
    
}

- (void) fileTransferServicesPathChangeComplete: (OBEXFileTransferServices*)inServices
                                          error: (OBEXError)inError
                                      finalPath: (NSString*)inPath
{
    Log("[PATH_Function]  entry - err: %d\n", inError );
    
    if( inError == kOBEXSuccess )
    {

        NSString *path = [NSString stringWithFormat:@"%@", [mTransferServices currentPath]];
        NSURL *url = [NSURL fileURLWithPath :path];

        [pathController setURL:url];
        [setPathTextField setStringValue:[mTransferServices currentPath]];
        //[mTransferServices changeCurrentFolderForwardToPath:[mTransferServices currentPath]];
        
        //[self log:@"New Current Path:"];
        //[self log:[mTransferServices currentPath]];

        NSLog(@"Changing path in fileTransferServicesPathChangeComplete");
        [mTransferServices retrieveFolderListing];

    }
}

- (void) fileTransferServicesRemoveItemComplete:(OBEXFileTransferServices*)inServices	error:(OBEXError)inError removedItem:(NSString*)file {
    
    Log("[REMOVE_Function]  entry - err: %d\n", inError );
    
    if( inError == kOBEXSuccess )
    {
        [mTransferServices retrieveFolderListing];
        
        NSString *path = [NSString stringWithFormat:@"%@", [mTransferServices currentPath]];
        NSURL *url = [NSURL fileURLWithPath :path];
        
        [pathController setURL:url];
        [setPathTextField setStringValue:[mTransferServices currentPath]];

    }
    
}

- (int) numberOfRowsInTableView:(NSTableView *)tv
{
    return	[mFTPCurrentDirectoryObjects count];
}

- (id) tableView:(NSTableView *)tv objectValueForTableColumn:(NSTableColumn *)tc row:(int)row {
    id object = nil;
    
    if( !mFTPCurrentDirectoryObjects || row == -1 ){ goto exit; }
    if( row >= [mFTPCurrentDirectoryObjects count]){ goto exit; }
    
    object = [mFTPCurrentDirectoryObjects objectAtIndex: row];
    
exit:
    
    return( object );
}

- (void) tableView:(NSTableView *)tv willDisplayCell:(id)cell forTableColumn:(NSTableColumn *)column row:(int)rowIndex {
    NSMutableString *	sizeString;
    NSMutableString *	tempString;
    NSMutableString *   typeString;
    int					fileType	= 0;
    NSNumber *			tempNumber;
    id object;
    
    if( tv != mFTPBrowseTable )
    {
        return;
    }
    if( !mFTPCurrentDirectoryObjects || rowIndex == -1 ){ goto exit; }
    
    
    NS_DURING
    
    object = [mFTPCurrentDirectoryObjects objectAtIndex: rowIndex];
    tempNumber = (NSNumber*) [(NSDictionary*)object objectForKey: (NSString*)kFTSListingTypeKey];
    
    if( tempNumber )
    {
        fileType = [tempNumber intValue];
    }
    else
    {
        fileType = kFTSFileTypeFile;
    }
    
    [cell setFont:[NSFont systemFontOfSize:10]];
    
    if( [(NSString*)[column identifier] compare:@"name"] == NSOrderedSame )
    {   // FILE NAME
        [cell setStringValue: [(NSDictionary*)object objectForKey: (NSString*)kFTSListingNameKey]];
    }
    
    else if( [(NSString*)[column identifier] compare:@"type"] == NSOrderedSame )
    {   // FILE TYPE
        
        sizeString = [(NSDictionary*)object objectForKey: (NSString*)kFTSListingSizeKey];
        
        if( !typeString || ( fileType == kFTSFileTypeFolder) )
        {
            
            [cell setStringValue:@"Folder"];

        }
        else
        {
            [cell setStringValue:@"File"];

        }
        
        [cell setStringValue:(NSString*)typeString];

    }
    
    else if( [(NSString*)[column identifier] compare:@"size"] == NSOrderedSame )
    {	// FILE SIZE
        
        tempString = [NSMutableString stringWithCapacity:10];
        sizeString = [(NSDictionary*)object objectForKey: (NSString*)kFTSListingSizeKey];
        
        if( !sizeString || ( fileType == kFTSFileTypeFolder ) )
        {
            [tempString appendString:@"N/A"];
        }
        else if( sizeString && [sizeString length] > 0 )
        {
            [tempString	appendString: sizeString];
        }
        
        [cell setStringValue:(NSString*)tempString];
        
    }
    
    NS_HANDLER
				
    NS_ENDHANDLER
    
exit:
    
    return;
}

- (BOOL)tabView:(NSTabView *)tabView shouldSelectTabViewItem:(NSTabViewItem *)tabViewItem {
    if( mTransferServices && [mTransferServices isConnected] )
    {
        return NO;
    }
    else
    {
        return YES;
    }
}

- (void) listFilesInBrowserFromList:(NSArray*)inObjects {
    
    Log("Listing all files and folders...\n");
    
    // Make sure we have a store for our browser data
    
    if( mFTPCurrentDirectoryObjects )
    {
        [mFTPCurrentDirectoryObjects release];
        mFTPCurrentDirectoryObjects = nil;
    }
    
    // Parse folder listing
    
    mFTPCurrentDirectoryObjects = [[NSMutableArray alloc] initWithArray: inObjects];
    require( mFTPCurrentDirectoryObjects, exit );
    
    // Sort the dictionary
    
    [mFTPBrowseTable selectColumn:0 byExtendingSelection:TRUE];
    [mFTPCurrentDirectoryObjects retain];
    [mFTPCurrentDirectoryObjects sortUsingFunction:ListingValuesSorter context:self];
    
exit:
    
    [mFTPBrowseTable reloadData];
    [mFTPBrowseTable selectRow:0 byExtendingSelection:TRUE];
    
    Log("Listing completed\n");
}

- (NSTableView *)ftpTable {
    return mFTPBrowseTable;
}

- (void)doubleClick:(NSArray *)selectedObjects {
    
    [self setPathAction:nil];
    
}


#pragma mark Sync Function

- (void)comparison {
    
    
    NSString *currentPath = [mTransferServices currentPath];
    
    // Set Path
    
    if(![currentPath isEqualToString:@"/"]) {
        
        // Set Path
        
        // Under progress... add here code for sync function
        
        
    }
    
}


@end

int ListingValuesSorter( id	object1, id object2, void* theContext ) {
    NSString*	compareString1	= nil;
    NSString*	compareString2	= nil;
    int			sortingColumn	= 0;
    int			returnValue		= 0;
    int			fileType1		= 0;
    int			fileType2		= 0;
    
    
    if( !object1 || !object2 || !theContext )
    {
        return( NSOrderedSame );
    }
    
    sortingColumn = [[((AppDelegate*)theContext) ftpTable] selectedColumn];
    
    if( sortingColumn != 1 ){ goto defaultCompareExit; }
    
    // try size comparison.
    
    fileType1 = [(NSNumber*)[(NSDictionary*)object1 objectForKey: (NSString*)kFTSListingSizeKey] intValue];
    fileType2 = [(NSNumber*)[(NSDictionary*)object2 objectForKey: (NSString*)kFTSListingSizeKey] intValue];
    
    if( fileType1 == fileType2 )
    {
        goto defaultCompareExit;
    }
    else
    {
        if( fileType1 > fileType2 )
        {
            returnValue = NSOrderedDescending;
        }
        else
        {
            returnValue = NSOrderedAscending;
        }
    }
    
    return( returnValue );
    
defaultCompareExit:
    
    // name column = 0
    {
        // Sort alpha by default.
        compareString1 = [(NSDictionary*)object1 objectForKey: (NSString*)kFTSListingNameKey];
        compareString2 = [(NSDictionary*)object2 objectForKey: (NSString*)kFTSListingNameKey];
        
        if( !compareString1 || !compareString2 ) return( NSOrderedSame );
        
        returnValue = [compareString1	compare:compareString2];
    }
    
    return( returnValue );
}