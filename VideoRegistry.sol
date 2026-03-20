// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract VideoRegistry {

    struct VideoInfo {
        string  deviceId;
        string  location;
        string  author;
        uint256 timestamp;
        bool    exists;
    }

    mapping(string => VideoInfo) private videos;
    string[] public allHashes;

    event VideoRegistered(
        string  videoHash,
        string  deviceId,
        string  location,
        string  author,
        uint256 timestamp
    );

    function register(
        string memory videoHash,
        string memory deviceId,
        string memory location,
        string memory author
    ) public {
        require(!videos[videoHash].exists, "Video already registered");
        videos[videoHash] = VideoInfo(deviceId, location, author, block.timestamp, true);
        allHashes.push(videoHash);
        emit VideoRegistered(videoHash, deviceId, location, author, block.timestamp);
    }

    function verify(string memory videoHash) public view returns (
        bool    exists,
        string memory deviceId,
        string memory location,
        string memory author,
        uint256 timestamp
    ) {
        VideoInfo memory info = videos[videoHash];
        return (info.exists, info.deviceId, info.location, info.author, info.timestamp);
    }

    function getTotalCount() public view returns (uint256) {
        return allHashes.length;
    }

    function getHashByIndex(uint256 index) public view returns (string memory) {
        return allHashes[index];
    }
}
