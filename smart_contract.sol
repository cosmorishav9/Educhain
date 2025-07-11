// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract CertificateManager {
    struct Certificate {
        string certId;
        string name;
        string course;
        string issueDate;
    }
    
    mapping(string => Certificate) public certificates;
    
    event CertificateIssued(string certId, string name, string course, string issueDate);
    
    function issueCertificate(string memory certId, string memory name, string memory course, string memory issueDate) public {
        certificates[certId] = Certificate(certId, name, course, issueDate);
        emit CertificateIssued(certId, name, course, issueDate);
    }
    
    function verifyCertificate(string memory certId) public view returns (string memory, string memory, string memory, string memory) {
        Certificate memory cert = certificates[certId];
        return (cert.certId, cert.name, cert.course, cert.issueDate);
    }
}

