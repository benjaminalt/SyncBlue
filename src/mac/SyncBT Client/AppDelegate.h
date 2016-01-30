
//  AppDelegate.h
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


// Libraries and frameworks

#import <Cocoa/Cocoa.h>

#import <IOBluetooth/IOBluetooth.h>
#import <IOBluetooth/objc/IOBluetoothOBEXSession.h>

#import <IOBluetooth/IOBluetoothUserLib.h>
#import <IOBluetooth/objc/IOBluetoothDevice.h>

#import <IOBluetooth/objc/IOBluetoothSDPUUID.h>
#import <IOBluetooth/objc/IOBluetoothRFCOMMChannel.h>
#import <IOBluetoothUI/objc/IOBluetoothDeviceSelectorController.h>

// Classes

@class BBBluetoothOBEXClient;
@class OBEXSession;
@class BBOBEXHeaderSet;
@class BBOBEXRequest;
@class IOBluetoothDevice;
@class BBOBEXResponse;
@class IOBluetoothRFCOMMChannel;
@class OBEXFileTransferServices;
@class FileSystemNode;

// Objects

@interface AppDelegate : NSWindow
{
    int counter;
    IOBluetoothRFCOMMChannel *mChannel;
    IOBluetoothUserNotification *mChannelNotif;
    IOBluetoothDevice *device;

    
    
    IOBluetoothDevice *mBluetoothDevice;
    IOBluetoothRFCOMMChannel *mRFCOMMChannel;
    IOBluetoothOBEXSession*	mOBEXSession;
    
    OBEXSession* mSession;
    id mDelegate;
    
    OBEXMaxPacketLength	mMaxPacketLength;
    int mLastServerResponse;
    uint32_t mConnectionID;
    BOOL mHasConnectionID;
    
    BOOL mAborting;
    
    BOOL					mUserWantsAbort;
    BOOL					mAbortSent;
    
    uint32_t				mLastFileOffset;
    
    CFMutableDataRef		mGetHeadersDataRef;
   	CFMutableDataRef		mPutHeadersDataRef;
   	CFMutableDataRef		mSetPathHeadersDataRef;
    NSData*					mTempPutDataBuffer;
    NSFileHandle*			mCurrentFile;
    UInt32					mCurrentFileSize;
    
    
    BBOBEXRequest *mCurrentRequest;
    
    // OBEX Session
    
    OBEXFileTransferServices *  mTransferServices;
    
    //---------
    
    //FTP browser
    
    IBOutlet id					mMainWindow;
    IBOutlet id					mTabView;
    IBOutlet id                 mBrowserInterface;
    IBOutlet id                 closeBrowserInterface;
    
    IBOutlet id                 browseDeviceButton;
    IBOutlet id					mOPPSendFileButton;
    //IBOutlet id					mOPPProgressIndicator;
    IBOutlet id					mOPPFileStatusField;
    IBOutlet id					mOPPFileTransferredField;
    IBOutlet id					mOPPFileRemainingField;
    
    IBOutlet NSArrayController *mContentArray;
    IBOutlet id					mFTPBrowseTable;
    IBOutlet id					mFTPConnectButton;
    IBOutlet id					mFTPGetButton;
    IBOutlet id					mFTPSendButton;
    
    int							mTestType;
    NSMutableArray *			mFTPCurrentDirectoryObjects;
    NSString *					mOPPSelectedFile;
    NSString *                  mFileToSend;
    NSNumber *                  mFileSizeToSend;
    unsigned                    length;
    unsigned                    totalLength;
    unsigned                    bytesSentOutofTotalLength;
    unsigned                    percentageProgress;
    
    // SyncBT Server Browser Mode
    
    IBOutlet NSArrayController *mContentArray2;
    IBOutlet id					mFTPBrowseTable2;

    
    //---------
    
    IBOutlet id pathController;
    IBOutlet id homeDirectoryButton;
    IBOutlet id upDirectoryButton;
    IBOutlet id setPathTextField;
    IBOutlet id connectionLog;
    IBOutlet id packetSize;
    IBOutlet id closeConnectionButton;
    IBOutlet id addConnectionButton;
    IBOutlet id abortButton;
    IBOutlet id addressField;
    IBOutlet id cancelButton;
    IBOutlet id channelField;
    IBOutlet id connectButton;
    IBOutlet id connectionProgress;
    IBOutlet id filePathField;
    IBOutlet id logTextView;
    IBOutlet id sendButton;
    IBOutlet id transferProgress;
    
    NSTimer *ConnectionTimer;
    
    IBOutlet id *numberOfRowsSelected;
    
@private
    IBOutlet NSBrowser *_browser;
    FileSystemNode *_rootNode;
    
}

// Properties

@property (strong, nonatomic) IBOutlet NSProgressIndicator *mOPPProgressIndicator;

- (IBAction)removeItem:(id)sender;
- (IBAction)setPathAction:(id)sender;
- (IBAction)upDirectory:(id)sender;
- (IBAction)homeDirectory:(id)sender;
- (IBAction)clear:(id)sender;

- (NSString *)getNameOfDevice;

- (IBAction)createFolder:(id)sender;
- (IBAction)closeBrowserInterface:(id)sender;
- (IBAction)openBrowserInterface:(id)sender;
- (IBAction)sendFileOPP:(id)sender;
- (IBAction)connectToFTP:(id)sender;
- (IBAction)getFileFTP:(id)sender;
- (IBAction)sendFileFTP:(id)sender;
- (IBAction)quit:(id)sender;

- (void)connect;
- (void)abortAction:(id)sender;
- (void)listFilesInBrowserFromList:(NSArray*)inObjects;
- (void)doubleClick:(NSArray *)selectedObjects;

- (NSTableView *)ftpTable;

- (void) sendData:(NSData*)inData
             type:(NSString*)inType
             name:(NSString*)inName;

@end
