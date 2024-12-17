// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

contract CredentialManager {
    address public admin;

    // Credential structure
    struct Credential {
        uint256 credentialId;
        address issuedTo;
        string details;
        bool isRevoked;
    }

    // Mapping to store credentials
    mapping(uint256 => Credential) public credentials;

    // Events
    event CredentialIssued(uint256 indexed credentialId, address indexed issuedTo, string details);
    event CredentialRevoked(uint256 indexed credentialId, address indexed revokedBy);

    // Modifier to restrict access to admin
    modifier onlyAdmin() {
        require(msg.sender == admin, "Only admin can perform this action.");
        _;
    }

    // Constructor: Sets the admin
    constructor() {
        admin = msg.sender; // Deployer is the admin
    }

    /**
     * @dev Issue a new credential.
     * @param _credentialId Unique identifier for the credential.
     * @param _issuedTo Address to whom the credential is issued.
     * @param _details Additional details about the credential.
     */
    function issueCredential(uint256 _credentialId, address _issuedTo, string memory _details) public onlyAdmin {
        require(credentials[_credentialId].credentialId == 0, "Credential already exists.");

        credentials[_credentialId] = Credential({
            credentialId: _credentialId,
            issuedTo: _issuedTo,
            details: _details,
            isRevoked: false
        });

        emit CredentialIssued(_credentialId, _issuedTo, _details);
    }

    /**
     * @dev Revoke a credential.
     * @param _credentialId Unique identifier for the credential.
     */
    function revokeCredential(uint256 _credentialId) public onlyAdmin {
        require(credentials[_credentialId].credentialId != 0, "Credential does not exist.");
        require(!credentials[_credentialId].isRevoked, "Credential is already revoked.");

        credentials[_credentialId].isRevoked = true;

        emit CredentialRevoked(_credentialId, msg.sender);
    }

    /**
     * @dev Check if a credential is revoked.
     * @param _credentialId Unique identifier for the credential.
     * @return Boolean indicating if the credential is revoked.
     */
    function isCredentialRevoked(uint256 _credentialId) public view returns (bool) {
        require(credentials[_credentialId].credentialId != 0, "Credential does not exist.");
        return credentials[_credentialId].isRevoked;
    }

    /**
     * @dev Get details of a credential.
     * @param _credentialId Unique identifier for the credential.
     * @return credentialId, issuedTo, details, isRevoked
     */
    function getCredentialDetails(uint256 _credentialId) public view returns (uint256, address, string memory, bool) {
        require(credentials[_credentialId].credentialId != 0, "Credential does not exist.");

        Credential memory cred = credentials[_credentialId];
        return (cred.credentialId, cred.issuedTo, cred.details, cred.isRevoked);
    }
}
